#!/bin/bash
# ABOUTME: Automated Docker development environment setup script
# ABOUTME: Validates prerequisites, stops conflicts, and starts services

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

# Check if running from project root
check_project_root() {
    log_info "Checking project root..."

    if [[ ! -f "docker-compose.yml" || ! -f "Makefile" ]]; then
        log_error "Must run from project root directory"
        log_info "Usage: ./scripts/setup-docker-dev.sh"
        exit 1
    fi

    log_success "Running from correct directory"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker not installed. Please install Docker Desktop or Docker Engine."
        exit 1
    fi

    # Check Docker Compose
    if ! docker compose version &> /dev/null; then
        log_error "Docker Compose not available. Please update Docker to a version with built-in compose."
        exit 1
    fi

    # Check Make
    if ! command -v make &> /dev/null; then
        log_error "Make not installed. Please install make."
        exit 1
    fi

    # Check Docker daemon
    if ! docker info &> /dev/null; then
        log_error "Docker daemon not running. Please start Docker."
        exit 1
    fi

    log_success "All prerequisites satisfied"
}

# Check for port conflicts
check_port_conflicts() {
    log_info "Checking for port conflicts..."

    local ports=(3000 5432 6379 8000)
    local conflicts=()

    for port in "${ports[@]}"; do
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            conflicts+=($port)
        fi
    done

    if [[ ${#conflicts[@]} -gt 0 ]]; then
        log_warning "Port conflicts detected on: ${conflicts[*]}"
        log_info "Attempting to stop local services..."

        # Try to stop common conflicting services
        for service in postgresql redis; do
            if systemctl is-active --quiet $service 2>/dev/null; then
                log_info "Stopping $service..."
                sudo systemctl stop $service || log_warning "Failed to stop $service"
            fi
        done

        # Check again
        local remaining_conflicts=()
        for port in "${conflicts[@]}"; do
            if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
                remaining_conflicts+=($port)
            fi
        done

        if [[ ${#remaining_conflicts[@]} -gt 0 ]]; then
            log_error "Ports still in use: ${remaining_conflicts[*]}"
            log_info "Please manually stop services using these ports:"
            for port in "${remaining_conflicts[@]}"; do
                echo "  Port $port: $(lsof -Pi :$port -sTCP:LISTEN -t | head -1 | xargs ps -p | tail -1)"
            done
            exit 1
        fi
    fi

    log_success "No port conflicts"
}

# Validate project configuration
validate_configuration() {
    log_info "Validating project configuration..."

    # Check Poetry files are in backend/
    if [[ ! -f "backend/pyproject.toml" ]]; then
        log_error "backend/pyproject.toml not found"
        exit 1
    fi

    if [[ ! -f "backend/poetry.lock" ]]; then
        log_error "backend/poetry.lock not found"
        exit 1
    fi

    # Check Poetry files are NOT in root
    if [[ -f "pyproject.toml" ]]; then
        log_error "pyproject.toml should not be in root directory"
        log_info "Poetry files must be in backend/ directory"
        exit 1
    fi

    # Validate Docker Compose configuration
    if ! docker compose config --quiet; then
        log_error "Invalid docker-compose.yml configuration"
        exit 1
    fi

    log_success "Project configuration valid"
}

# Setup environment file
setup_environment() {
    log_info "Setting up environment configuration..."

    if [[ ! -f ".env" ]]; then
        if [[ -f ".env.example" ]]; then
            log_info "Copying .env.example to .env..."
            cp .env.example .env
            log_warning "Please edit .env file with your actual API keys:"
            log_info "  - GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET"
            log_info "  - GEMINI_API_KEY"
            log_info "  - Generate JWT_SECRET_KEY with: python -c \"import secrets; print(secrets.token_hex(32))\""
        else
            log_error ".env.example file not found"
            exit 1
        fi
    else
        log_info ".env file already exists"
    fi

    log_success "Environment configuration ready"
}

# Build and start services
build_and_start() {
    log_info "Building Docker containers..."

    # Clean build to avoid caching issues
    docker compose build --no-cache

    log_info "Starting services..."
    docker compose up -d

    log_info "Waiting for services to be healthy..."

    # Wait for services with timeout
    local timeout=120
    local elapsed=0
    local interval=5

    while [[ $elapsed -lt $timeout ]]; do
        if make health &>/dev/null; then
            log_success "All services are healthy!"
            break
        fi

        sleep $interval
        elapsed=$((elapsed + interval))
        log_info "Waiting... ($elapsed/${timeout}s)"
    done

    if [[ $elapsed -ge $timeout ]]; then
        log_error "Services failed to become healthy within ${timeout}s"
        log_info "Check service logs with: make logs"
        exit 1
    fi
}

# Display service information
show_service_info() {
    log_success "Development environment ready!"
    echo
    log_info "Service URLs:"
    echo "  🌐 Frontend:    http://localhost:3000"
    echo "  🚀 Backend API: http://localhost:8000"
    echo "  📚 API Docs:    http://localhost:8000/docs"
    echo
    log_info "Useful commands:"
    echo "  make health     # Check service health"
    echo "  make logs       # View all logs"
    echo "  make down       # Stop services"
    echo "  make restart    # Restart services"
    echo
    log_info "Next steps:"
    echo "  1. Edit .env file with your API keys"
    echo "  2. Visit http://localhost:3000 to see the app"
    echo "  3. Read DEVELOPMENT.md for detailed guide"
}

# Main execution
main() {
    echo
    log_info "🚀 Setting up Snowflake MCP Lambda Docker development environment..."
    echo

    check_project_root
    check_prerequisites
    check_port_conflicts
    validate_configuration
    setup_environment
    build_and_start
    show_service_info

    echo
    log_success "🎉 Docker setup complete! Happy coding!"
}

# Run main function
main "$@"
