#!/bin/bash

# ABOUTME: Production deployment script for Snowflake MCP Lambda
# ABOUTME: Handles build, security scanning, deployment, and health checks with error handling

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
COMPOSE_FILE="$PROJECT_ROOT/docker-compose.prod.yml"
ENV_FILE="$PROJECT_ROOT/.env.prod"
BACKUP_DIR="$PROJECT_ROOT/backups"
LOG_FILE="$PROJECT_ROOT/logs/deploy-$(date +%Y%m%d-%H%M%S).log"

# Ensure log directory exists
mkdir -p "$(dirname "$LOG_FILE")"
mkdir -p "$BACKUP_DIR"

# Logging function
log() {
    local level=$1
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${timestamp} [${level}] ${message}" | tee -a "$LOG_FILE"
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

# Error handling
cleanup() {
    local exit_code=$?
    if [[ $exit_code -ne 0 ]]; then
        error "Deployment failed with exit code $exit_code"
        error "Check logs at: $LOG_FILE"

        # Attempt to restore from backup if available
        if [[ -f "$BACKUP_DIR/docker-compose.backup.yml" ]]; then
            warn "Attempting to restore from backup..."
            docker compose -f "$BACKUP_DIR/docker-compose.backup.yml" up -d || true
        fi
    fi
}

trap cleanup EXIT

# Validate prerequisites
validate_prerequisites() {
    info "Validating prerequisites..."

    # Check required commands
    local required_commands=("docker" "curl" "jq")
    for cmd in "${required_commands[@]}"; do
        if ! command -v "$cmd" &> /dev/null; then
            error "Required command '$cmd' not found"
            exit 1
        fi
    done

    # Check docker compose (v2 plugin)
    if ! docker compose version &> /dev/null; then
        error "Docker Compose plugin not found. Please install docker-compose-plugin"
        exit 1
    fi

    # Check Docker daemon
    if ! docker info &> /dev/null; then
        error "Docker daemon is not running"
        exit 1
    fi

    # Check environment file
    if [[ ! -f "$ENV_FILE" ]]; then
        error "Environment file not found: $ENV_FILE"
        error "Please create $ENV_FILE with required variables"
        exit 1
    fi

    # Validate environment variables
    source "$ENV_FILE"
    local required_vars=("POSTGRES_PASSWORD" "SECRET_KEY" "GOOGLE_CLIENT_ID" "GOOGLE_CLIENT_SECRET")
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var:-}" ]]; then
            error "Required environment variable '$var' not set"
            exit 1
        fi
    done

    success "Prerequisites validated"
}

# Backup current deployment
backup_deployment() {
    info "Creating deployment backup..."

    local backup_timestamp=$(date +%Y%m%d-%H%M%S)
    local backup_subdir="$BACKUP_DIR/$backup_timestamp"

    mkdir -p "$backup_subdir"

    # Backup docker-compose file
    if [[ -f "$COMPOSE_FILE" ]]; then
        cp "$COMPOSE_FILE" "$backup_subdir/docker-compose.backup.yml"
    fi

    # Backup environment file
    if [[ -f "$ENV_FILE" ]]; then
        cp "$ENV_FILE" "$backup_subdir/.env.backup"
    fi

    # Export database if possible
    if docker compose -f "$COMPOSE_FILE" ps postgres 2>/dev/null | grep -q "Up"; then
        info "Backing up database..."
        docker compose -f "$COMPOSE_FILE" exec -T postgres pg_dump -U postgres snowflake_mcp > "$backup_subdir/database.sql" || warn "Database backup failed"
    fi

    # Keep only last 5 backups
    find "$BACKUP_DIR" -maxdepth 1 -type d -name "20*" | sort -r | tail -n +6 | xargs -r rm -rf

    success "Backup created: $backup_subdir"
}

# Build images
build_images() {
    info "Building Docker images..."

    # Set version from git or environment
    local version="${VERSION:-$(git rev-parse --short HEAD 2>/dev/null || echo 'latest')}"
    export VERSION="$version"

    info "Building version: $version"

    # Build images with cache
    docker compose -f "$COMPOSE_FILE" build --parallel --progress=plain

    success "Images built successfully"
}

# Security scanning
security_scan() {
    info "Running security scans..."

    # Check if Trivy is available
    if command -v trivy &> /dev/null; then
        info "Scanning images with Trivy..."

        # Scan backend image
        local backend_image="snowflake-mcp-backend:${VERSION:-latest}"
        trivy image --exit-code 1 --severity HIGH,CRITICAL "$backend_image" || {
            error "Security scan failed for $backend_image"
            exit 1
        }

        success "Security scan passed"
    else
        warn "Trivy not available, skipping security scan"
        warn "Install Trivy for production deployments: https://aquasecurity.github.io/trivy/"
    fi
}

# Deploy services
deploy_services() {
    info "Deploying services..."

    # Load environment variables
    set -a
    source "$ENV_FILE"
    set +a

    # Create data directories
    mkdir -p "$PROJECT_ROOT/data/postgres" "$PROJECT_ROOT/data/redis"

    # Deploy with rolling update
    docker compose -f "$COMPOSE_FILE" up -d --remove-orphans

    success "Services deployed"
}

# Health checks
health_checks() {
    info "Running health checks..."

    local max_attempts=30
    local attempt=1
    local services=("backend" "postgres" "redis")

    # Wait for services to be healthy
    for service in "${services[@]}"; do
        info "Checking health of $service..."

        while [[ $attempt -le $max_attempts ]]; do
            if docker compose -f "$COMPOSE_FILE" ps "$service" | grep -q "healthy"; then
                success "$service is healthy"
                break
            elif [[ $attempt -eq $max_attempts ]]; then
                error "$service failed to become healthy"
                # Show logs for debugging
                docker compose -f "$COMPOSE_FILE" logs --tail=50 "$service"
                exit 1
            else
                info "Waiting for $service to be healthy (attempt $attempt/$max_attempts)..."
                sleep 10
                ((attempt++))
            fi
        done

        attempt=1
    done

    # Test API endpoint
    info "Testing API endpoints..."
    local api_url="http://localhost:8000"

    # Test health endpoint
    if curl -f -s "$api_url/health" > /dev/null; then
        success "API health check passed"
    else
        error "API health check failed"
        exit 1
    fi

    # Test API documentation
    if curl -f -s "$api_url/docs" > /dev/null; then
        success "API documentation accessible"
    else
        warn "API documentation not accessible"
    fi

    success "All health checks passed"
}

# Cleanup old resources
cleanup_resources() {
    info "Cleaning up unused resources..."

    # Remove unused images
    docker image prune -f

    # Remove unused volumes (be careful with this in production)
    # docker volume prune -f

    # Remove unused networks
    docker network prune -f

    success "Resource cleanup completed"
}

# Post-deployment verification
post_deployment_verification() {
    info "Running post-deployment verification..."

    # Check container resource usage
    info "Container resource usage:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"

    # Check logs for errors
    info "Checking recent logs for errors..."
    if docker compose -f "$COMPOSE_FILE" logs --tail=100 2>&1 | grep -i error | head -5; then
        warn "Errors found in logs - please review"
    else
        success "No errors found in recent logs"
    fi

    # Performance test
    info "Running basic performance test..."
    local response_time=$(curl -w "%{time_total}" -s -o /dev/null "http://localhost:8000/health")
    if (( $(echo "$response_time < 1.0" | bc -l) )); then
        success "API response time: ${response_time}s"
    else
        warn "API response time is slow: ${response_time}s"
    fi

    success "Post-deployment verification completed"
}

# Main deployment flow
main() {
    info "Starting deployment process..."

    validate_prerequisites
    backup_deployment
    build_images
    security_scan
    deploy_services
    health_checks
    cleanup_resources
    post_deployment_verification

    success "Deployment completed successfully!"
    info "Application is available at: http://localhost:8000"
    info "API documentation: http://localhost:8000/docs"
    info "Logs are available at: $LOG_FILE"
}

# Handle script arguments
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "backup")
        validate_prerequisites
        backup_deployment
        ;;
    "health")
        health_checks
        ;;
    "logs")
        docker compose -f "$COMPOSE_FILE" logs -f
        ;;
    "stop")
        info "Stopping services..."
        docker compose -f "$COMPOSE_FILE" down
        success "Services stopped"
        ;;
    "restart")
        info "Restarting services..."
        docker compose -f "$COMPOSE_FILE" restart
        health_checks
        success "Services restarted"
        ;;
    *)
        echo "Usage: $0 {deploy|backup|health|logs|stop|restart}"
        echo "  deploy  - Full deployment process (default)"
        echo "  backup  - Create backup only"
        echo "  health  - Run health checks only"
        echo "  logs    - Follow application logs"
        echo "  stop    - Stop all services"
        echo "  restart - Restart all services"
        exit 1
        ;;
esac
