#!/bin/bash
# ABOUTME: Comprehensive development environment setup script for Data Chat MVP
# ABOUTME: Installs all necessary tools and dependencies for new developers

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running on macOS or Linux
detect_os() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        log_info "Detected macOS"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        log_info "Detected Linux"
    else
        log_error "Unsupported operating system: $OSTYPE"
        exit 1
    fi
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Install Homebrew on macOS
install_homebrew() {
    if [[ "$OS" == "macos" ]]; then
        if ! command_exists brew; then
            log_info "Installing Homebrew..."
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            
            # Add Homebrew to PATH for Apple Silicon Macs
            if [[ $(uname -m) == "arm64" ]]; then
                echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zshrc
                eval "$(/opt/homebrew/bin/brew shellenv)"
            fi
            
            log_success "Homebrew installed successfully"
        else
            log_info "Homebrew already installed"
            brew update
        fi
    fi
}

# Install Docker
install_docker() {
    if ! command_exists docker; then
        log_info "Installing Docker..."
        
        if [[ "$OS" == "macos" ]]; then
            if command_exists brew; then
                brew install --cask docker
                log_info "Docker installed via Homebrew. Please start Docker Desktop manually."
            else
                log_warning "Please install Docker Desktop manually from https://www.docker.com/products/docker-desktop"
            fi
        elif [[ "$OS" == "linux" ]]; then
            # Install Docker on Linux
            curl -fsSL https://get.docker.com -o get-docker.sh
            sudo sh get-docker.sh
            sudo usermod -aG docker $USER
            
            # Install Docker Compose
            sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
            sudo chmod +x /usr/local/bin/docker-compose
            
            log_success "Docker installed. Please log out and back in to use Docker without sudo."
        fi
    else
        log_info "Docker already installed"
    fi
}

# Install Python and Poetry
install_python_poetry() {
    # Check Python version
    if command_exists python3; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        log_info "Python $PYTHON_VERSION found"
        
        # Check if Python version is 3.8+
        if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
            log_success "Python version is compatible"
        else
            log_error "Python 3.8+ required. Please install a newer version."
            exit 1
        fi
    else
        log_info "Installing Python..."
        if [[ "$OS" == "macos" ]]; then
            brew install python@3.11
        elif [[ "$OS" == "linux" ]]; then
            sudo apt-get update
            sudo apt-get install -y python3 python3-pip python3-venv
        fi
    fi
    
    # Install Poetry
    if ! command_exists poetry; then
        log_info "Installing Poetry..."
        curl -sSL https://install.python-poetry.org | python3 -
        
        # Add Poetry to PATH
        export PATH="$HOME/.local/bin:$PATH"
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
        
        log_success "Poetry installed successfully"
    else
        log_info "Poetry already installed"
    fi
}

# Install Node.js and npm
install_nodejs() {
    if ! command_exists node; then
        log_info "Installing Node.js..."
        
        if [[ "$OS" == "macos" ]]; then
            brew install node
        elif [[ "$OS" == "linux" ]]; then
            # Install NodeSource repository
            curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
            sudo apt-get install -y nodejs
        fi
        
        log_success "Node.js installed successfully"
    else
        NODE_VERSION=$(node --version)
        log_info "Node.js $NODE_VERSION already installed"
    fi
    
    # Update npm to latest version
    if command_exists npm; then
        log_info "Updating npm to latest version..."
        npm install -g npm@latest
    fi
}

# Install development tools
install_dev_tools() {
    log_info "Installing development tools..."
    
    if [[ "$OS" == "macos" ]]; then
        brew install git curl wget jq
    elif [[ "$OS" == "linux" ]]; then
        sudo apt-get install -y git curl wget jq build-essential
    fi
    
    # Install pre-commit
    if ! command_exists pre-commit; then
        log_info "Installing pre-commit..."
        pip3 install pre-commit
        log_success "pre-commit installed successfully"
    else
        log_info "pre-commit already installed"
    fi
}

# Setup project environment
setup_project_environment() {
    log_info "Setting up project environment..."
    
    # Copy environment file if it doesn't exist
    if [[ ! -f .env ]]; then
        if [[ -f .env.example ]]; then
            cp .env.example .env
            log_success "Environment file created from .env.example"
            log_warning "Please edit .env file with your actual configuration values"
        else
            log_warning "No .env.example found. You may need to create .env manually"
        fi
    else
        log_info ".env file already exists"
    fi
    
    # Install backend dependencies
    if [[ -f backend/pyproject.toml ]]; then
        log_info "Installing backend dependencies..."
        cd backend
        poetry install
        cd ..
        log_success "Backend dependencies installed"
    fi
    
    # Install frontend dependencies
    if [[ -f frontend/package.json ]]; then
        log_info "Installing frontend dependencies..."
        cd frontend
        npm install
        cd ..
        log_success "Frontend dependencies installed"
    fi
    
    # Setup pre-commit hooks
    if [[ -f .pre-commit-config.yaml ]]; then
        log_info "Installing pre-commit hooks..."
        pre-commit install
        log_success "Pre-commit hooks installed"
    fi
}

# Validate installation
validate_installation() {
    log_info "Validating installation..."
    
    local errors=0
    
    # Check Docker
    if command_exists docker; then
        if docker --version >/dev/null 2>&1; then
            log_success "Docker: $(docker --version)"
        else
            log_error "Docker installed but not running"
            errors=$((errors + 1))
        fi
    else
        log_error "Docker not found"
        errors=$((errors + 1))
    fi
    
    # Check Docker Compose
    if command_exists docker && docker compose version >/dev/null 2>&1; then
        log_success "Docker Compose: $(docker compose version)"
    else
        log_error "Docker Compose not available"
        errors=$((errors + 1))
    fi
    
    # Check Python
    if command_exists python3; then
        log_success "Python: $(python3 --version)"
    else
        log_error "Python not found"
        errors=$((errors + 1))
    fi
    
    # Check Poetry
    if command_exists poetry; then
        log_success "Poetry: $(poetry --version)"
    else
        log_error "Poetry not found"
        errors=$((errors + 1))
    fi
    
    # Check Node.js
    if command_exists node; then
        log_success "Node.js: $(node --version)"
    else
        log_error "Node.js not found"
        errors=$((errors + 1))
    fi
    
    # Check npm
    if command_exists npm; then
        log_success "npm: $(npm --version)"
    else
        log_error "npm not found"
        errors=$((errors + 1))
    fi
    
    if [[ $errors -eq 0 ]]; then
        log_success "All tools installed successfully!"
        return 0
    else
        log_error "$errors tool(s) failed to install properly"
        return 1
    fi
}

# Print next steps
print_next_steps() {
    log_info "
=============================================================================
🎉 SETUP COMPLETE! Next steps:
=============================================================================

1. Configure your environment:
   - Edit .env file with your actual API keys and credentials
   - Get Google OAuth credentials from https://console.cloud.google.com/
   - Get Gemini API key from https://makersuite.google.com/app/apikey

2. Start the development environment:
   make dev-setup          # Full setup with health checks
   make up                 # Start all services
   make wait-healthy       # Wait for services to be ready

3. Run tests:
   make test              # Backend tests
   make test-frontend     # Frontend tests
   make test-all          # All tests

4. Development workflow:
   make logs              # View all logs
   make shell-backend     # Backend container shell
   make shell-frontend    # Frontend container shell

5. Quality checks:
   make lint-frontend     # Frontend linting
   make type-check-frontend # TypeScript checking
   pre-commit run --all-files # All quality checks

6. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

For more information, see:
- README.md - Project overview
- DEVELOPMENT.md - Development guide
- CLAUDE.md - AI assistant instructions

Happy coding! 🚀
"
}

# Main execution
main() {
    log_info "Starting Data Chat MVP development environment setup..."
    
    detect_os
    install_homebrew
    install_docker
    install_python_poetry
    install_nodejs
    install_dev_tools
    setup_project_environment
    
    if validate_installation; then
        print_next_steps
        log_success "Setup completed successfully!"
        exit 0
    else
        log_error "Setup completed with errors. Please review the output above."
        exit 1
    fi
}

# Run main function
main "$@"