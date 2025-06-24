#!/bin/bash

# Flask Application Docker Build Script
# Usage: ./docker/build_docker.sh [OPTIONS] or cd docker && ./build_docker.sh [OPTIONS]
# Options:
#   --dev     Build development image (default)
#   --prod    Build production image
#   --clean   Clean build (remove existing images/containers)
#   --deploy  Build and deploy to remote server
#   --help    Show this help message

set -e  # Exit on any error

# Script configuration
IMAGE_NAME="jira-flask-app"
IMAGE_TAG="latest"
CONTAINER_NAME="jira-flask-container"
REMOTE_HOST="10.102.99.22"
REMOTE_USER="peter-lin"  # Updated to your username
DOCKER_REGISTRY=""  # Add your registry if using one

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
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

show_help() {
    echo "Flask Application Docker Build Script"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --dev      Build development image (default)"
    echo "  --prod     Build production image"
    echo "  --clean    Clean build (remove existing images/containers)"
    echo "  --deploy   Build and deploy to remote server"
    echo "  --push     Push image to registry"
    echo "  --help     Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./docker/build_docker.sh                    # Build development image"
    echo "  ./docker/build_docker.sh --prod            # Build production image"
    echo "  ./docker/build_docker.sh --clean --prod    # Clean build production image"
    echo "  ./docker/build_docker.sh --deploy          # Build and deploy to VM"
}

check_dependencies() {
    log_info "Checking dependencies..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_warning "Docker Compose is not installed"
        log_info "You can still build with docker build command"
    fi
    
    log_success "Dependencies check passed"
}

clean_docker() {
    log_info "Cleaning existing Docker containers and images..."
    
    # Stop and remove container if running
    if docker ps -q -f name=$CONTAINER_NAME | grep -q .; then
        log_info "Stopping container: $CONTAINER_NAME"
        docker stop $CONTAINER_NAME
    fi
    
    if docker ps -a -q -f name=$CONTAINER_NAME | grep -q .; then
        log_info "Removing container: $CONTAINER_NAME"
        docker rm $CONTAINER_NAME
    fi
    
    # Remove image if exists
    if docker images -q $IMAGE_NAME:$IMAGE_TAG | grep -q .; then
        log_info "Removing image: $IMAGE_NAME:$IMAGE_TAG"
        docker rmi $IMAGE_NAME:$IMAGE_TAG
    fi
    
    # Clean up dangling images
    if docker images -f "dangling=true" -q | grep -q .; then
        log_info "Removing dangling images..."
        docker rmi $(docker images -f "dangling=true" -q) 2>/dev/null || true
    fi
    
    log_success "Docker cleanup completed"
}

build_image() {
    local env_type=$1
    
    log_info "Building Docker image for $env_type environment..."
    
    # Create .dockerignore if it doesn't exist
    if [ ! -f .dockerignore ]; then
        log_info "Creating .dockerignore file..."
        cp docker/.dockerignore .dockerignore 2>/dev/null || cat > .dockerignore << EOF
.git
.gitignore
README.md
FEATURES.md
CLAUDE.md
.env
.venv
venv/
__pycache__
*.pyc
*.pyo
*.pyd
.pytest_cache
.coverage
htmlcov/
.tox/
.cache
.mypy_cache
.DS_Store
Thumbs.db
*.log
logs/
node_modules/
.dockerfile
docker-compose.override.yml
EOF
    fi
    
    # Build the image
    if [ "$env_type" = "production" ]; then
        IMAGE_TAG="prod"
        log_info "Building production image with tag: $IMAGE_NAME:$IMAGE_TAG"
        docker build -f docker/Dockerfile -t $IMAGE_NAME:$IMAGE_TAG \
            --build-arg FLASK_ENV=production \
            --build-arg PORT=5002 \
            .
    else
        IMAGE_TAG="dev"
        log_info "Building development image with tag: $IMAGE_NAME:$IMAGE_TAG"
        docker build -f docker/Dockerfile -t $IMAGE_NAME:$IMAGE_TAG \
            --build-arg FLASK_ENV=development \
            --build-arg PORT=5002 \
            .
    fi
    
    log_success "Docker image built successfully: $IMAGE_NAME:$IMAGE_TAG"
    
    # Show image info
    log_info "Image details:"
    docker images $IMAGE_NAME:$IMAGE_TAG
}

test_image() {
    log_info "Testing Docker image..."
    
    # Run container for testing
    CONTAINER_ID=$(docker run -d -p 5002:5002 --name ${CONTAINER_NAME}-test $IMAGE_NAME:$IMAGE_TAG)
    
    # Wait for container to start
    sleep 5
    
    # Test if application is responding
    if curl -f http://localhost:5002/ > /dev/null 2>&1; then
        log_success "Application is responding correctly"
    else
        log_error "Application test failed"
        docker logs ${CONTAINER_NAME}-test
        docker stop ${CONTAINER_NAME}-test
        docker rm ${CONTAINER_NAME}-test
        exit 1
    fi
    
    # Clean up test container
    docker stop ${CONTAINER_NAME}-test
    docker rm ${CONTAINER_NAME}-test
    
    log_success "Image test completed successfully"
}

push_image() {
    if [ -z "$DOCKER_REGISTRY" ]; then
        log_warning "No Docker registry configured. Skipping push."
        return
    fi
    
    log_info "Pushing image to registry..."
    
    # Tag for registry
    docker tag $IMAGE_NAME:$IMAGE_TAG $DOCKER_REGISTRY/$IMAGE_NAME:$IMAGE_TAG
    
    # Push to registry
    docker push $DOCKER_REGISTRY/$IMAGE_NAME:$IMAGE_TAG
    
    log_success "Image pushed to registry: $DOCKER_REGISTRY/$IMAGE_NAME:$IMAGE_TAG"
}

deploy_to_vm() {
    log_info "Deploying to VM: $REMOTE_HOST"
    
    # Check if we can connect to the VM
    if ! ssh -o ConnectTimeout=5 $REMOTE_USER@$REMOTE_HOST "echo 'SSH connection successful'" > /dev/null 2>&1; then
        log_error "Cannot connect to $REMOTE_HOST via SSH"
        log_info "Please ensure:"
        log_info "1. SSH keys are set up"
        log_info "2. VM is accessible"
        log_info "3. User has Docker permissions"
        exit 1
    fi
    
    # Save image to tar file
    log_info "Saving Docker image to tar file..."
    docker save $IMAGE_NAME:$IMAGE_TAG > ${IMAGE_NAME}-${IMAGE_TAG}.tar
    
    # Copy image to VM
    log_info "Copying image to VM..."
    scp ${IMAGE_NAME}-${IMAGE_TAG}.tar $REMOTE_USER@$REMOTE_HOST:/tmp/
    
    # Copy docker-compose.yml and .env files
    log_info "Copying configuration files..."
    scp docker/docker-compose.yml $REMOTE_USER@$REMOTE_HOST:/tmp/
    if [ -f .env ]; then
        scp .env $REMOTE_USER@$REMOTE_HOST:/tmp/
    fi
    
    # Load and run image on VM
    log_info "Loading and starting application on VM..."
    ssh $REMOTE_USER@$REMOTE_HOST << EOF
        cd /tmp
        
        # Load the image
        docker load < ${IMAGE_NAME}-${IMAGE_TAG}.tar
        
        # Stop existing container if running
        docker stop $CONTAINER_NAME 2>/dev/null || true
        docker rm $CONTAINER_NAME 2>/dev/null || true
        
        # Run the new container
        docker run -d \
            --name $CONTAINER_NAME \
            -p 5002:5002 \
            --restart unless-stopped \
            $IMAGE_NAME:$IMAGE_TAG
        
        # Clean up
        rm ${IMAGE_NAME}-${IMAGE_TAG}.tar
        
        # Show status
        echo "Container status:"
        docker ps | grep $CONTAINER_NAME
EOF
    
    # Clean up local tar file
    rm ${IMAGE_NAME}-${IMAGE_TAG}.tar
    
    log_success "Deployment completed successfully!"
    log_info "Application should be available at: http://$REMOTE_HOST:5002"
}

run_with_compose() {
    log_info "Starting application with Docker Compose..."
    
    if command -v docker-compose &> /dev/null; then
        docker-compose -f docker/docker-compose.yml up -d
    elif command -v docker &> /dev/null && docker compose version &> /dev/null; then
        docker compose -f docker/docker-compose.yml up -d
    else
        log_error "Docker Compose not available"
        exit 1
    fi
    
    log_success "Application started with Docker Compose"
    log_info "Available at: http://localhost:5002"
}

# Main script logic
main() {
    # Determine if we're running from project root or docker directory
    local script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    local project_root=""
    
    if [[ "$(basename "$script_dir")" == "docker" ]]; then
        # Running from docker directory
        project_root="$(dirname "$script_dir")"
        log_info "Running from docker directory, project root: $project_root"
    else
        # Running from project root
        project_root="$script_dir"
        log_info "Running from project root: $project_root"
    fi
    
    # Change to project root for Docker build context
    cd "$project_root"
    
    local clean_build=false
    local env_type="development"
    local deploy=false
    local push=false
    local use_compose=false
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --dev)
                env_type="development"
                shift
                ;;
            --prod)
                env_type="production"
                shift
                ;;
            --clean)
                clean_build=true
                shift
                ;;
            --deploy)
                deploy=true
                shift
                ;;
            --push)
                push=true
                shift
                ;;
            --compose)
                use_compose=true
                shift
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # Print script header
    echo "========================================"
    echo "Flask Application Docker Build Script"
    echo "========================================"
    echo ""
    
    # Check dependencies
    check_dependencies
    
    # Clean if requested
    if [ "$clean_build" = true ]; then
        clean_docker
    fi
    
    # Use Docker Compose if requested
    if [ "$use_compose" = true ]; then
        run_with_compose
        exit 0
    fi
    
    # Build image
    build_image $env_type
    
    # Test image
    test_image
    
    # Push to registry if requested
    if [ "$push" = true ]; then
        push_image
    fi
    
    # Deploy if requested
    if [ "$deploy" = true ]; then
        deploy_to_vm
    else
        log_success "Build completed successfully!"
        log_info "To run the container locally:"
        log_info "  docker run -d -p 5002:5002 --name $CONTAINER_NAME $IMAGE_NAME:$IMAGE_TAG"
        log_info ""
        log_info "To deploy to VM:"
        log_info "  $0 --deploy"
        log_info ""
        log_info "To use Docker Compose:"
        log_info "  ./docker/build_docker.sh --compose"
    fi
}

# Run main function with all arguments
main "$@"