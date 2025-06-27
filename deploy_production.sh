#!/bin/bash
# Production Deployment Script for 10.102.99.22
# This script builds and deploys the SONiC Feature Management System to production

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

echo "=========================================="
echo "Production Deployment to 10.102.99.22"
echo "SONiC Feature Management System"
echo "=========================================="
echo ""

# Check if production environment file exists
if [ ! -f ".env.production" ]; then
    log_error "Production environment file (.env.production) not found!"
    log_info "Please create .env.production with production database settings"
    exit 1
fi

# Confirm deployment
echo "This will deploy to production server: 10.102.99.22"
echo "The application will be available at: http://10.102.99.22:5002"
echo ""
read -p "Are you sure you want to deploy to production? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    log_info "Deployment cancelled"
    exit 0
fi

# Run the Docker build and deployment
log_info "Starting production build and deployment..."
./docker/build_docker.sh --prod --clean --deploy

if [ $? -eq 0 ]; then
    log_success "Production deployment completed successfully!"
    echo ""
    log_info "Application URLs:"
    log_info "  Main App: http://10.102.99.22:5002"
    log_info "  Feature Matrix: http://10.102.99.22:5002/feature-list"
    log_info "  Database Info: http://10.102.99.22:5002/db-info"
    echo ""
    log_info "To check container status on production:"
    log_info "  ssh peter-lin@10.102.99.22 'docker ps | grep jira-flask'"
    echo ""
    log_info "To view application logs:"
    log_info "  ssh peter-lin@10.102.99.22 'docker logs jira-flask-container'"
else
    log_error "Production deployment failed!"
    exit 1
fi