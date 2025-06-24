#!/bin/bash

# Standalone Deployment Script for Flask App
# Deploys to VM without Docker requirement

set -e

# Configuration
REMOTE_HOST="10.102.99.22"
REMOTE_USER="peter-lin"
APP_DIR="/home/peter-lin/jira-app"
PYTHON_VERSION="python3"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# Function to test SSH connection
test_ssh() {
    log_info "Testing SSH connection to $REMOTE_USER@$REMOTE_HOST..."
    if ssh -o ConnectTimeout=10 -o BatchMode=yes $REMOTE_USER@$REMOTE_HOST "echo 'SSH connection successful'" > /dev/null 2>&1; then
        log_success "SSH connection working"
        return 0
    else
        log_error "SSH connection failed"
        return 1
    fi
}

# Function to prepare remote environment
prepare_remote_env() {
    log_info "Preparing remote environment..."
    
    ssh $REMOTE_USER@$REMOTE_HOST "
        # Create app directory in user home
        mkdir -p $APP_DIR
        
        # Check Python version
        echo 'Python version:'
        python3 --version
        
        # Check if required tools are available
        if command -v python3 &> /dev/null; then
            echo 'Python3 is available'
        else
            echo 'Warning: Python3 not found'
        fi
        
        if command -v pip3 &> /dev/null; then
            echo 'pip3 is available'
        else
            echo 'Warning: pip3 not found'
        fi
        
        echo 'Remote environment prepared'
    "
}

# Function to transfer application files
transfer_files() {
    log_info "Transferring application files..."
    
    # Create a temporary tar file with all necessary files
    tar czf /tmp/jira-app.tar.gz \
        --exclude='.git' \
        --exclude='venv' \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        --exclude='*.log' \
        --exclude='.dockerignore' \
        --exclude='docker/' \
        --exclude='minimal.py' \
        --exclude='test_app.py' \
        .
    
    # Transfer to remote
    scp /tmp/jira-app.tar.gz $REMOTE_USER@$REMOTE_HOST:$APP_DIR/
    
    # Clean up local temp file
    rm /tmp/jira-app.tar.gz
    
    log_success "Files transferred successfully"
}

# Function to setup application on remote
setup_remote_app() {
    log_info "Setting up application on remote server..."
    
    ssh $REMOTE_USER@$REMOTE_HOST "
        cd $APP_DIR
        
        # Extract application files
        tar xzf jira-app.tar.gz
        rm jira-app.tar.gz
        
        # Create virtual environment
        python3 -m venv venv
        
        # Activate virtual environment and install dependencies
        source venv/bin/activate
        pip install --upgrade pip
        pip install -r requirements.txt
        
        # Create a simple start script instead of systemd service
        cat > start_flask.sh <<'EOF'
#!/bin/bash
cd /home/peter-lin/jira-app
source venv/bin/activate
export FLASK_ENV=production
export PYTHONPATH=/home/peter-lin/jira-app
nohup python app.py > flask_app.log 2>&1 &
echo $! > flask_app.pid
echo "Flask app started with PID: $(cat flask_app.pid)"
EOF
        chmod +x start_flask.sh
        
        # Create stop script
        cat > stop_flask.sh <<'EOF'
#!/bin/bash
cd /home/peter-lin/jira-app
if [ -f flask_app.pid ]; then
    PID=$(cat flask_app.pid)
    if kill -0 $PID 2>/dev/null; then
        kill $PID
        echo "Flask app stopped (PID: $PID)"
        rm flask_app.pid
    else
        echo "Flask app not running"
        rm flask_app.pid
    fi
else
    echo "No PID file found"
fi
EOF
        chmod +x stop_flask.sh
        
        echo 'Application setup completed'
    "
}

# Function to start the application
start_app() {
    log_info "Starting Flask application..."
    
    ssh $REMOTE_USER@$REMOTE_HOST "
        cd $APP_DIR
        
        # Stop any existing flask app
        ./stop_flask.sh 2>/dev/null || true
        
        # Start the application
        ./start_flask.sh
        
        # Wait a moment for startup
        sleep 3
        
        # Check if process is running
        if [ -f flask_app.pid ] && kill -0 \\\$(cat flask_app.pid) 2>/dev/null; then
            echo 'Flask application is running with PID:' \\\$(cat flask_app.pid)
        else
            echo 'Warning: Flask application may not have started properly'
        fi
        
        # Check if port 5002 is listening
        if netstat -tlnp 2>/dev/null | grep :5002; then
            echo 'Application is listening on port 5002'
        else
            echo 'Warning: Port 5002 not detected'
        fi
    "
}

# Function to test the deployed application
test_deployment() {
    log_info "Testing deployed application..."
    
    # Wait a moment for the app to fully start
    sleep 5
    
    # Test from remote server
    ssh $REMOTE_USER@$REMOTE_HOST "
        # Test local access
        if curl -s http://localhost:5002 > /dev/null; then
            echo 'Local access test: SUCCESS'
        else
            echo 'Local access test: FAILED'
        fi
        
        # Show application logs
        echo 'Recent application logs:'
        if [ -f $APP_DIR/flask_app.log ]; then
            tail -10 $APP_DIR/flask_app.log
        else
            echo 'No log file found'
        fi
    "
    
    # Test external access
    log_info "Testing external access..."
    if curl -s --max-time 10 http://$REMOTE_HOST:5002 > /dev/null; then
        log_success "External access test: SUCCESS"
        log_success "Application deployed successfully!"
        log_info "Access your application at: http://$REMOTE_HOST:5002"
    else
        log_warning "External access test failed - check firewall settings"
        log_info "You may need to configure firewall rules (requires sudo):"
        log_info "  sudo ufw allow 5002"
    fi
}

# Function to show deployment status
show_status() {
    log_info "Application status:"
    ssh $REMOTE_USER@$REMOTE_HOST "
        cd $APP_DIR
        
        echo 'Application status:'
        if [ -f flask_app.pid ] && kill -0 \\\$(cat flask_app.pid) 2>/dev/null; then
            echo 'Flask app is running with PID:' \\\$(cat flask_app.pid)
        else
            echo 'Flask app is not running'
        fi
        
        echo 'Listening ports:'
        netstat -tlnp 2>/dev/null | grep :5002 || echo 'Port 5002 not listening'
        
        echo 'Process info:'
        ps aux | grep '[p]ython.*app.py' || echo 'Flask process not found'
        
        echo 'Recent logs:'
        if [ -f flask_app.log ]; then
            tail -5 flask_app.log
        else
            echo 'No log file found'
        fi
    "
}

# Function to manage the application
manage_app() {
    case $1 in
        start)
            ssh $REMOTE_USER@$REMOTE_HOST "cd $APP_DIR && ./start_flask.sh"
            log_success "Application started"
            ;;
        stop)
            ssh $REMOTE_USER@$REMOTE_HOST "cd $APP_DIR && ./stop_flask.sh"
            log_success "Application stopped"
            ;;
        restart)
            ssh $REMOTE_USER@$REMOTE_HOST "cd $APP_DIR && ./stop_flask.sh && ./start_flask.sh"
            log_success "Application restarted"
            ;;
        status)
            show_status
            ;;
        logs)
            ssh $REMOTE_USER@$REMOTE_HOST "cd $APP_DIR && tail -f flask_app.log"
            ;;
        *)
            echo "Usage: $0 {start|stop|restart|status|logs}"
            ;;
    esac
}

# Main deployment function
deploy() {
    echo "========================================"
    echo "Flask Application Standalone Deployment"
    echo "========================================"
    echo ""
    
    # Test SSH connection
    if ! test_ssh; then
        log_error "Cannot connect to remote server. Please check SSH configuration."
        exit 1
    fi
    
    # Prepare remote environment
    prepare_remote_env
    
    # Transfer files
    transfer_files
    
    # Setup application
    setup_remote_app
    
    # Start application
    start_app
    
    # Test deployment
    test_deployment
    
    echo ""
    log_success "Deployment completed!"
    log_info "Use '$0 status' to check application status"
    log_info "Use '$0 logs' to view application logs"
    log_info "Use '$0 restart' to restart the application"
}

# Main script logic
case ${1:-deploy} in
    deploy)
        deploy
        ;;
    start|stop|restart|status|logs)
        manage_app $1
        ;;
    *)
        echo "Flask Application Deployment Script"
        echo ""
        echo "Usage: $0 [COMMAND]"
        echo ""
        echo "Commands:"
        echo "  deploy    Deploy application (default)"
        echo "  start     Start the application"
        echo "  stop      Stop the application"
        echo "  restart   Restart the application"
        echo "  status    Show application status"
        echo "  logs      Show application logs"
        ;;
esac