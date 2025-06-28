#!/bin/bash

# ABOUTME: Security scanning script for Docker images and containers
# ABOUTME: Performs vulnerability assessment, security benchmarks, and compliance checks

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
SCAN_RESULTS_DIR="$PROJECT_ROOT/security-reports"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

# Create results directory
mkdir -p "$SCAN_RESULTS_DIR"

# Logging functions
log() {
    local level=$1
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${timestamp} [${level}] ${message}"
}

info() {
    log "INFO" "${BLUE}$*${NC}"
}

warn() {
    log "WARN" "${YELLOW}$*${NC}"
}

error() {
    log "ERROR" "${RED}$*${NC}"
}

success() {
    log "SUCCESS" "${GREEN}$*${NC}"
}

# Check if required tools are available
check_security_tools() {
    info "Checking security scanning tools..."

    local tools_available=0

    # Check for Trivy
    if command -v trivy &> /dev/null; then
        info "Trivy found: $(trivy --version | head -1)"
        tools_available=$((tools_available + 1))
    else
        warn "Trivy not found. Install: https://aquasecurity.github.io/trivy/"
    fi

    # Check for Docker Bench Security
    if [[ -f "/usr/local/bin/docker-bench-security.sh" ]] || command -v docker-bench-security &> /dev/null; then
        info "Docker Bench Security found"
        tools_available=$((tools_available + 1))
    else
        warn "Docker Bench Security not found. Install: https://github.com/docker/docker-bench-security"
    fi

    # Check for Hadolint
    if command -v hadolint &> /dev/null; then
        info "Hadolint found: $(hadolint --version)"
        tools_available=$((tools_available + 1))
    else
        warn "Hadolint not found. Install: https://github.com/hadolint/hadolint"
    fi

    if [[ $tools_available -eq 0 ]]; then
        error "No security scanning tools found. Please install at least one."
        exit 1
    fi

    success "$tools_available security tools available"
}

# Scan Dockerfiles for best practices
scan_dockerfiles() {
    info "Scanning Dockerfiles for security best practices..."

    local dockerfiles=()
    mapfile -t dockerfiles < <(find "$PROJECT_ROOT" -name "Dockerfile*" -type f)

    if [[ ${#dockerfiles[@]} -eq 0 ]]; then
        warn "No Dockerfiles found"
        return
    fi

    for dockerfile in "${dockerfiles[@]}"; do
        info "Scanning: $dockerfile"

        if command -v hadolint &> /dev/null; then
            local output_file="$SCAN_RESULTS_DIR/hadolint-$(basename "$dockerfile")-$TIMESTAMP.txt"

            if hadolint "$dockerfile" > "$output_file" 2>&1; then
                success "Hadolint scan passed for $(basename "$dockerfile")"
            else
                warn "Hadolint found issues in $(basename "$dockerfile"). See: $output_file"
                cat "$output_file"
            fi
        fi

        # Custom security checks
        info "Running custom security checks on $(basename "$dockerfile")..."
        local issues=0

        # Check for non-root user
        if ! grep -q "USER " "$dockerfile"; then
            warn "$(basename "$dockerfile"): No USER instruction found (running as root)"
            issues=$((issues + 1))
        fi

        # Check for HEALTHCHECK
        if ! grep -q "HEALTHCHECK" "$dockerfile"; then
            warn "$(basename "$dockerfile"): No HEALTHCHECK instruction found"
            issues=$((issues + 1))
        fi

        # Check for secrets in environment variables
        if grep -i "password\|secret\|key\|token" "$dockerfile" | grep -v "ENV.*=\$"; then
            warn "$(basename "$dockerfile"): Potential secrets found in environment variables"
            issues=$((issues + 1))
        fi

        # Check for latest tag usage
        if grep -q "FROM.*:latest" "$dockerfile"; then
            warn "$(basename "$dockerfile"): Using 'latest' tag is not recommended"
            issues=$((issues + 1))
        fi

        if [[ $issues -eq 0 ]]; then
            success "Custom security checks passed for $(basename "$dockerfile")"
        else
            warn "Found $issues security issues in $(basename "$dockerfile")"
        fi
    done
}

# Scan Docker images for vulnerabilities
scan_images() {
    info "Scanning Docker images for vulnerabilities..."

    local images=()
    mapfile -t images < <(docker images --format "{{.Repository}}:{{.Tag}}" | grep -E "snowflake-mcp|postgres|redis|nginx" | head -10)

    if [[ ${#images[@]} -eq 0 ]]; then
        warn "No relevant Docker images found"
        return
    fi

    for image in "${images[@]}"; do
        info "Scanning image: $image"

        if command -v trivy &> /dev/null; then
            local output_file="$SCAN_RESULTS_DIR/trivy-$(echo "$image" | tr '/:' '_')-$TIMESTAMP.json"

            info "Running Trivy scan..."
            if trivy image --format json --output "$output_file" "$image"; then
                # Parse results
                local critical=$(jq '.Results[]?.Vulnerabilities[]? | select(.Severity=="CRITICAL") | .VulnerabilityID' "$output_file" 2>/dev/null | wc -l)
                local high=$(jq '.Results[]?.Vulnerabilities[]? | select(.Severity=="HIGH") | .VulnerabilityID' "$output_file" 2>/dev/null | wc -l)
                local medium=$(jq '.Results[]?.Vulnerabilities[]? | select(.Severity=="MEDIUM") | .VulnerabilityID' "$output_file" 2>/dev/null | wc -l)

                info "Scan results for $image:"
                info "  Critical: $critical"
                info "  High: $high"
                info "  Medium: $medium"

                if [[ $critical -gt 0 ]]; then
                    error "CRITICAL vulnerabilities found in $image"
                    # Show critical vulnerabilities
                    jq -r '.Results[]?.Vulnerabilities[]? | select(.Severity=="CRITICAL") | "  - \(.VulnerabilityID): \(.Title)"' "$output_file" 2>/dev/null || true
                elif [[ $high -gt 5 ]]; then
                    warn "High number of HIGH severity vulnerabilities in $image ($high)"
                else
                    success "Acceptable vulnerability level for $image"
                fi
            else
                error "Trivy scan failed for $image"
            fi
        else
            warn "Skipping vulnerability scan (Trivy not available)"
        fi
    done
}

# Run Docker Bench Security
run_docker_bench() {
    info "Running Docker Bench Security..."

    local bench_script=""

    # Try to find Docker Bench Security
    if [[ -f "/usr/local/bin/docker-bench-security.sh" ]]; then
        bench_script="/usr/local/bin/docker-bench-security.sh"
    elif command -v docker-bench-security &> /dev/null; then
        bench_script="docker-bench-security"
    else
        # Try to run from Docker
        info "Running Docker Bench Security from container..."
        docker run --rm --net host --pid host --userns host --cap-add audit_control \
            -e DOCKER_CONTENT_TRUST=$DOCKER_CONTENT_TRUST \
            -v /var/lib:/var/lib:ro \
            -v /var/run/docker.sock:/var/run/docker.sock:ro \
            -v /usr/lib/systemd:/usr/lib/systemd:ro \
            -v /etc:/etc:ro \
            --label docker_bench_security \
            docker/docker-bench-security > "$SCAN_RESULTS_DIR/docker-bench-$TIMESTAMP.txt" 2>&1

        info "Docker Bench Security results saved to: $SCAN_RESULTS_DIR/docker-bench-$TIMESTAMP.txt"
        return
    fi

    if [[ -n "$bench_script" ]]; then
        "$bench_script" > "$SCAN_RESULTS_DIR/docker-bench-$TIMESTAMP.txt" 2>&1
        info "Docker Bench Security results saved to: $SCAN_RESULTS_DIR/docker-bench-$TIMESTAMP.txt"

        # Parse results
        local warnings=$(grep -c "WARN" "$SCAN_RESULTS_DIR/docker-bench-$TIMESTAMP.txt" || echo "0")
        local fails=$(grep -c "FAIL" "$SCAN_RESULTS_DIR/docker-bench-$TIMESTAMP.txt" || echo "0")

        info "Docker Bench results: $warnings warnings, $fails failures"

        if [[ $fails -gt 0 ]]; then
            warn "Docker Bench Security found $fails failures"
        else
            success "Docker Bench Security check passed"
        fi
    fi
}

# Check container runtime security
check_container_runtime() {
    info "Checking container runtime security..."

    # Check if containers are running as root
    info "Checking for containers running as root..."
    local root_containers=()
    mapfile -t root_containers < <(docker ps --format "{{.Names}}" | xargs -I {} docker exec {} whoami 2>/dev/null | grep -n "root" | cut -d: -f1 || true)

    if [[ ${#root_containers[@]} -gt 0 ]]; then
        warn "Containers running as root detected"
        for container in "${root_containers[@]}"; do
            warn "  - Container running as root (check runtime configuration)"
        done
    else
        success "No containers running as root"
    fi

    # Check for privileged containers
    info "Checking for privileged containers..."
    local privileged_containers=()
    mapfile -t privileged_containers < <(docker ps --filter "status=running" --format "{{.Names}}" | xargs -I {} docker inspect {} --format "{{.Name}}: {{.HostConfig.Privileged}}" | grep "true" | cut -d: -f1 || true)

    if [[ ${#privileged_containers[@]} -gt 0 ]]; then
        warn "Privileged containers detected:"
        for container in "${privileged_containers[@]}"; do
            warn "  - $container"
        done
    else
        success "No privileged containers found"
    fi

    # Check network configuration
    info "Checking container network security..."
    local host_network_containers=()
    mapfile -t host_network_containers < <(docker ps --filter "status=running" --format "{{.Names}}" | xargs -I {} docker inspect {} --format "{{.Name}}: {{.HostConfig.NetworkMode}}" | grep "host" | cut -d: -f1 || true)

    if [[ ${#host_network_containers[@]} -gt 0 ]]; then
        warn "Containers using host network detected:"
        for container in "${host_network_containers[@]}"; do
            warn "  - $container"
        done
    else
        success "No containers using host network"
    fi
}

# Generate security report
generate_report() {
    info "Generating security report..."

    local report_file="$SCAN_RESULTS_DIR/security-report-$TIMESTAMP.md"

    cat > "$report_file" << EOF
# Security Scan Report

**Generated:** $(date)
**Project:** Snowflake MCP Lambda
**Scan ID:** $TIMESTAMP

## Summary

This report contains the results of security scanning performed on the Snowflake MCP Lambda Docker production setup.

## Scanned Components

- Docker images
- Dockerfiles
- Container runtime configuration
- Docker daemon configuration

## Scan Results

### Dockerfile Security (Hadolint)
$(ls "$SCAN_RESULTS_DIR"/hadolint-*.txt 2>/dev/null | wc -l) Dockerfile(s) scanned.

### Image Vulnerabilities (Trivy)
$(ls "$SCAN_RESULTS_DIR"/trivy-*.json 2>/dev/null | wc -l) image(s) scanned.

### Docker Bench Security
$(ls "$SCAN_RESULTS_DIR"/docker-bench-*.txt 2>/dev/null | wc -l) benchmark(s) executed.

## Recommendations

1. Regularly update base images to latest security patches
2. Review and address any CRITICAL and HIGH severity vulnerabilities
3. Follow Docker security best practices
4. Implement image signing and verification
5. Use minimal base images (e.g., Alpine, Distroless)
6. Regularly rotate secrets and certificates

## Files Generated

EOF

    # List all generated files
    find "$SCAN_RESULTS_DIR" -name "*$TIMESTAMP*" -type f | while read -r file; do
        echo "- $(basename "$file")" >> "$report_file"
    done

    success "Security report generated: $report_file"
}

# Main security scan function
main() {
    info "Starting security scan..."

    check_security_tools
    scan_dockerfiles
    scan_images
    run_docker_bench
    check_container_runtime
    generate_report

    success "Security scan completed!"
    info "Results available in: $SCAN_RESULTS_DIR"

    # Return non-zero if critical issues found
    local critical_files=$(find "$SCAN_RESULTS_DIR" -name "*$TIMESTAMP*" -type f -exec grep -l "CRITICAL\|FAIL" {} \; 2>/dev/null | wc -l)
    if [[ $critical_files -gt 0 ]]; then
        warn "Critical security issues found. Review the reports before deployment."
        exit 1
    fi
}

# Handle script arguments
case "${1:-scan}" in
    "scan")
        main
        ;;
    "clean")
        info "Cleaning old security reports..."
        find "$SCAN_RESULTS_DIR" -type f -mtime +7 -delete
        success "Old reports cleaned"
        ;;
    "report")
        generate_report
        ;;
    *)
        echo "Usage: $0 {scan|clean|report}"
        echo "  scan   - Run full security scan (default)"
        echo "  clean  - Clean old security reports"
        echo "  report - Generate security report only"
        exit 1
        ;;
esac
