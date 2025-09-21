#!/bin/bash
# Agent A Production Deployment Script

set -e

echo "🚀 Starting Agent A Production Deployment"
echo "=============================================="

# Configuration
SERVICE_NAME="agent-a"
DOCKER_IMAGE="agent-a:latest"
CONTAINER_NAME="agent-a-service"
PORT="8001"
LOG_DIR="./logs"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    log_info "Prerequisites check passed ✅"
}

# Create necessary directories
setup_directories() {
    log_info "Setting up directories..."
    
    mkdir -p logs
    mkdir -p monitoring
    mkdir -p docker
    
    log_info "Directories created ✅"
}

# Build Docker image
build_image() {
    log_info "Building Docker image..."
    
    cd docker
    docker build -t $DOCKER_IMAGE .
    cd ..
    
    log_info "Docker image built ✅"
}

# Stop existing container
stop_existing() {
    log_info "Stopping existing container..."
    
    if docker ps -q -f name=$CONTAINER_NAME | grep -q .; then
        docker stop $CONTAINER_NAME
        docker rm $CONTAINER_NAME
        log_info "Existing container stopped and removed ✅"
    else
        log_info "No existing container found ✅"
    fi
}

# Deploy with Docker Compose
deploy_compose() {
    log_info "Deploying with Docker Compose..."
    
    cd docker
    docker-compose up -d
    cd ..
    
    log_info "Docker Compose deployment completed ✅"
}

# Health check
health_check() {
    log_info "Performing health check..."
    
    # Wait for service to start
    sleep 10
    
    # Check if service is responding
    for i in {1..30}; do
        if curl -f http://localhost:$PORT/ &> /dev/null; then
            log_info "Health check passed ✅"
            return 0
        fi
        log_warn "Health check attempt $i/30 failed, retrying in 2 seconds..."
        sleep 2
    done
    
    log_error "Health check failed after 30 attempts"
    return 1
}

# Setup monitoring
setup_monitoring() {
    log_info "Setting up monitoring..."
    
    # Start metrics collection
    python monitoring/metrics_collector.py &
    
    log_info "Monitoring setup completed ✅"
}

# Show deployment status
show_status() {
    log_info "Deployment Status:"
    echo "=================="
    
    # Container status
    if docker ps -q -f name=$CONTAINER_NAME | grep -q .; then
        log_info "Container Status: Running ✅"
    else
        log_error "Container Status: Not Running ❌"
    fi
    
    # Service health
    if curl -f http://localhost:$PORT/ &> /dev/null; then
        log_info "Service Health: Healthy ✅"
    else
        log_error "Service Health: Unhealthy ❌"
    fi
    
    # Port status
    if netstat -tuln | grep -q ":$PORT "; then
        log_info "Port $PORT: Listening ✅"
    else
        log_error "Port $PORT: Not Listening ❌"
    fi
    
    echo ""
    log_info "Service URL: http://localhost:$PORT"
    log_info "API Documentation: http://localhost:$PORT/docs"
    log_info "Health Check: http://localhost:$PORT/"
}

# Main deployment process
main() {
    log_info "Starting deployment process..."
    
    check_prerequisites
    setup_directories
    build_image
    stop_existing
    deploy_compose
    
    if health_check; then
        setup_monitoring
        show_status
        log_info "🎉 Deployment completed successfully!"
    else
        log_error "❌ Deployment failed during health check"
        exit 1
    fi
}

# Run main function
main "$@"
