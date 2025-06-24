#!/bin/bash

# Simple deployment script without sudo requirements
set -e

REMOTE_HOST="10.102.99.22"
REMOTE_USER="peter-lin"
APP_DIR="/home/peter-lin/jira-app"

echo "Deploying Flask app to $REMOTE_USER@$REMOTE_HOST..."

# Test SSH connection
echo "Testing SSH connection..."
ssh -o ConnectTimeout=10 $REMOTE_USER@$REMOTE_HOST "echo 'SSH connection successful'"

# Create app directory and transfer files
echo "Creating app directory and transferring files..."
ssh $REMOTE_USER@$REMOTE_HOST "mkdir -p $APP_DIR"

# Create tar file and transfer
tar czf /tmp/jira-app.tar.gz \
    --exclude='.git' \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='*.log' \
    --exclude='docker/' \
    .

scp /tmp/jira-app.tar.gz $REMOTE_USER@$REMOTE_HOST:$APP_DIR/
rm /tmp/jira-app.tar.gz

# Setup and start application
echo "Setting up application..."
ssh $REMOTE_USER@$REMOTE_HOST "
    cd $APP_DIR
    tar xzf jira-app.tar.gz
    rm jira-app.tar.gz
    
    # Check if we can create virtual environment
    if ! python3 -m venv test_venv 2>/dev/null; then
        echo \"Virtual environment creation failed. Installing without venv...\"
        rm -rf test_venv
        
        # Install packages directly with pip3
        pip3 install --user -r requirements.txt
        
        # Create start script without venv
        cat > start_app.sh << 'SCRIPT_EOF2'
#!/bin/bash
cd /home/peter-lin/jira-app
export FLASK_ENV=production
export PATH=\$HOME/.local/bin:\$PATH
nohup python3 app.py > app.log 2>&1 &
echo \$! > app.pid
echo \"Flask app started with PID: \$(cat app.pid)\"
SCRIPT_EOF2
    else
        rm -rf test_venv
        echo \"Creating virtual environment...\"
        python3 -m venv venv
        source venv/bin/activate
        pip install --upgrade pip
        pip install -r requirements.txt
        
        # Create start script with venv
        cat > start_app.sh << 'SCRIPT_EOF3'
#!/bin/bash
cd /home/peter-lin/jira-app
source venv/bin/activate
export FLASK_ENV=production
nohup python3 app.py > app.log 2>&1 &
echo \$! > app.pid
echo \"Flask app started with PID: \$(cat app.pid)\"
SCRIPT_EOF3
    fi
    
    chmod +x start_app.sh
    
    # Create stop script  
    cat > stop_app.sh << 'SCRIPT_EOF'
#!/bin/bash
cd /home/peter-lin/jira-app
if [ -f app.pid ]; then
    PID=\$(cat app.pid)
    if kill -0 \$PID 2>/dev/null; then
        kill \$PID
        echo \"Flask app stopped (PID: \$PID)\"
        rm app.pid
    else
        echo \"Flask app not running\"
        rm app.pid
    fi
else
    echo \"No PID file found\"
fi
SCRIPT_EOF
    chmod +x stop_app.sh
    
    # Stop any existing app and start new one
    ./stop_app.sh 2>/dev/null || true
    ./start_app.sh
    
    sleep 3
    
    # Check status
    if [ -f app.pid ] && kill -0 \$(cat app.pid) 2>/dev/null; then
        echo \"Flask app is running with PID: \$(cat app.pid)\"
    else
        echo \"Warning: Flask app may not have started\"
    fi
    
    # Check port
    if netstat -tlnp 2>/dev/null | grep :5002; then
        echo \"Port 5002 is listening\"
    else
        echo \"Warning: Port 5002 not detected\"
    fi
"

echo "Testing application..."
sleep 2
if curl -s --max-time 10 http://$REMOTE_HOST:5002 > /dev/null; then
    echo "SUCCESS: Application is accessible at http://$REMOTE_HOST:5002"
else
    echo "WARNING: External access failed - check firewall settings"
    echo "You may need to run: sudo ufw allow 5002"
fi

echo "Deployment completed!"
echo "To manage the app:"
echo "  ssh $REMOTE_USER@$REMOTE_HOST 'cd $APP_DIR && ./start_app.sh'"
echo "  ssh $REMOTE_USER@$REMOTE_HOST 'cd $APP_DIR && ./stop_app.sh'"