# Deployment Guide

This guide provides step-by-step instructions for building, deploying, and running the Flask application on your development VM at 10.102.99.22.

## 📋 Prerequisites

### Local Machine Requirements
- Docker installed and running
- Git repository cloned
- SSH access to the target VM
- Network connectivity to 10.102.99.22

### VM Requirements (10.102.99.22)
- Docker installed and running
- SSH server enabled
- User with Docker permissions
- Port 5002 available

---

## 🚀 Quick Deployment (Automated)

For a complete automated deployment, use the build script:

```bash
# From project root - Build production image and deploy to VM
./docker/build_docker.sh --prod --deploy

# Alternative: Clean build and deploy
./docker/build_docker.sh --clean --prod --deploy
```

This will automatically:
1. Build the production Docker image
2. Test the image locally
3. Transfer the image to your VM
4. Start the container on the VM
5. Clean up temporary files

---

## 📖 Manual Step-by-Step Deployment

If you prefer manual control over each step:

### Step 1: Prepare SSH Access

First, ensure you can connect to your VM:

```bash
# Test SSH connection
ssh root@10.102.99.22 "echo 'Connection successful'"

# If using key-based authentication, ensure your key is loaded
ssh-add ~/.ssh/your_private_key
```

**Note**: Update the username in `docker/build_docker.sh` if not using `root`:
```bash
# Edit this line in the script
REMOTE_USER="your_username"  # Change from "root" to your username
```

### Step 2: Build Docker Image

Build the production-ready Docker image:

```bash
# From project root
cd /path/to/your/jira/project

# Build production image
./docker/build_docker.sh --prod

# Or build with clean slate (removes existing images)
./docker/build_docker.sh --clean --prod
```

**Expected Output:**
```
[INFO] Building Docker image for production environment...
[INFO] Building production image with tag: jira-flask-app:prod
[SUCCESS] Docker image built successfully: jira-flask-app:prod
[INFO] Testing Docker image...
[SUCCESS] Application is responding correctly
[SUCCESS] Image test completed successfully
```

### Step 3: Verify Local Image

Check that the image was built successfully:

```bash
# List Docker images
docker images | grep jira-flask-app

# Test run locally (optional)
docker run -d -p 5002:5002 --name test-container jira-flask-app:prod

# Test the application
curl http://localhost:5002

# Clean up test container
docker stop test-container && docker rm test-container
```

### Step 4: Prepare VM Environment

Connect to your VM and prepare the environment:

```bash
# SSH to VM
ssh root@10.102.99.22

# Check Docker is running
sudo systemctl status docker

# Check if port 5002 is available
sudo netstat -tlnp | grep :5002

# Create application directory (optional)
mkdir -p /opt/jira-app
cd /opt/jira-app

# Exit VM for now
exit
```

### Step 5: Transfer Image to VM

From your local machine, transfer the Docker image:

```bash
# Save image to tar file
docker save jira-flask-app:prod > jira-flask-app-prod.tar

# Copy to VM
scp jira-flask-app-prod.tar root@10.102.99.22:/tmp/

# Copy configuration files
scp docker/docker-compose.yml root@10.102.99.22:/tmp/

# Copy environment file (if exists)
scp .env root@10.102.99.22:/tmp/ 2>/dev/null || echo "No .env file found"

# Clean up local tar file
rm jira-flask-app-prod.tar
```

### Step 6: Deploy on VM

SSH to your VM and deploy the application:

```bash
# SSH to VM
ssh root@10.102.99.22

# Navigate to temp directory
cd /tmp

# Load the Docker image
docker load < jira-flask-app-prod.tar

# Verify image loaded
docker images | grep jira-flask-app

# Stop any existing container
docker stop jira-flask-container 2>/dev/null || true
docker rm jira-flask-container 2>/dev/null || true

# Run the new container
docker run -d \
    --name jira-flask-container \
    -p 5002:5002 \
    --restart unless-stopped \
    jira-flask-app:prod

# Clean up
rm jira-flask-app-prod.tar

# Check container status
docker ps | grep jira-flask-container
```

### Step 7: Verify Deployment

Test that the application is running correctly:

```bash
# From VM - Test local access
curl http://localhost:5002

# Check container logs
docker logs jira-flask-container

# Check container health
docker exec jira-flask-container ps aux

# Exit VM
exit
```

**From your local machine or browser:**
```bash
# Test external access
curl http://10.102.99.22:5002

# Or open in browser
open http://10.102.99.22:5002
```

---

## 🐳 Using Docker Compose (Alternative Method)

If you prefer using Docker Compose:

### Step 1: Transfer Files to VM

```bash
# Copy docker-compose.yml to VM
scp docker/docker-compose.yml root@10.102.99.22:/opt/jira-app/

# Copy environment file
scp .env root@10.102.99.22:/opt/jira-app/ 2>/dev/null || echo "No .env file"

# Transfer entire docker directory
scp -r docker/ root@10.102.99.22:/opt/jira-app/
```

### Step 2: Deploy with Docker Compose

```bash
# SSH to VM
ssh root@10.102.99.22

# Navigate to app directory
cd /opt/jira-app

# Build and start with Docker Compose
docker-compose -f docker/docker-compose.yml up -d

# Check status
docker-compose -f docker/docker-compose.yml ps

# View logs
docker-compose -f docker/docker-compose.yml logs -f
```

---

## 🔧 Configuration Options

### Environment Variables

Create a `.env` file in your project root for custom configuration:

```bash
# .env file
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-here

# Database URLs (update as needed)
PRIMARY_PROD_DB_URL=postgresql://user:password@db:5432/jira_primary
ANALYTICS_PROD_DB_URL=postgresql://user:password@db:5432/jira_analytics
CACHE_PROD_DB_URL=redis://redis:6379/0

# Optional: Database passwords
POSTGRES_PASSWORD=your-db-password
```

### Custom Ports

To run on a different port:

```bash
# Edit docker/build_docker.sh
# Change this line:
docker run -d -p 5003:5002 --name jira-flask-container jira-flask-app:prod

# Or update docker-compose.yml:
ports:
  - "5003:5002"
```

---

## 📊 Monitoring & Management

### Container Management Commands

```bash
# View running containers
docker ps

# View all containers
docker ps -a

# Check container logs
docker logs jira-flask-container

# Follow logs in real-time
docker logs -f jira-flask-container

# Get container stats
docker stats jira-flask-container

# Execute commands in container
docker exec -it jira-flask-container bash

# Restart container
docker restart jira-flask-container

# Stop container
docker stop jira-flask-container

# Remove container
docker rm jira-flask-container
```

### Application Logs

The application creates several log files:

```bash
# View request logs (inside container)
docker exec jira-flask-container cat /app/requests.log

# Monitor logs in real-time
docker exec jira-flask-container tail -f /app/requests.log
```

### Health Checks

```bash
# Check application health
curl http://10.102.99.22:5002/

# Check all routes
curl http://10.102.99.22:5002/about
curl http://10.102.99.22:5002/db-info
curl http://10.102.99.22:5002/sonic-switch

# Check container health
docker inspect jira-flask-container | grep Health -A 10
```

---

## 🚨 Troubleshooting

### Common Issues

#### 1. SSH Connection Failed
```bash
# Check SSH service on VM
ssh root@10.102.99.22 "sudo systemctl status sshd"

# Check network connectivity
ping 10.102.99.22

# Verify SSH key permissions
chmod 600 ~/.ssh/your_private_key
```

#### 2. Docker Build Failed
```bash
# Check Docker is running
sudo systemctl status docker

# Clean Docker cache
docker system prune -a

# Check disk space
df -h

# Rebuild with verbose output
docker build -f docker/Dockerfile -t jira-flask-app:prod . --no-cache
```

#### 3. Container Won't Start
```bash
# Check container logs
docker logs jira-flask-container

# Check port conflicts
sudo netstat -tlnp | grep :5002

# Check Docker daemon
sudo systemctl status docker

# Try running without daemon mode
docker run -it jira-flask-app:prod
```

#### 4. Application Not Accessible
```bash
# Check container is running
docker ps | grep jira-flask-container

# Check port mapping
docker port jira-flask-container

# Check firewall (if applicable)
sudo ufw status
sudo iptables -L

# Test from VM locally
ssh root@10.102.99.22 "curl http://localhost:5002"
```

### Log Locations

- **Container Logs**: `docker logs jira-flask-container`
- **Application Logs**: `/app/requests.log` (inside container)
- **Docker Daemon Logs**: `/var/log/docker.log` (on VM)

---

## 🔄 Updates & Maintenance

### Deploying Updates

When you make changes to your application:

```bash
# 1. Commit and push changes
git add .
git commit -m "Your changes"
git push

# 2. Rebuild and redeploy
./docker/build_docker.sh --clean --prod --deploy
```

### Backup & Recovery

```bash
# Backup container data
docker exec jira-flask-container tar czf /tmp/backup.tar.gz /app/data

# Copy backup from container
docker cp jira-flask-container:/tmp/backup.tar.gz ./backup-$(date +%Y%m%d).tar.gz

# Backup image
docker save jira-flask-app:prod | gzip > jira-flask-app-backup.tar.gz
```

### Performance Tuning

```bash
# Monitor resource usage
docker stats jira-flask-container

# Limit container resources
docker run -d \
    --name jira-flask-container \
    --memory=512m \
    --cpus=1.0 \
    -p 5002:5002 \
    jira-flask-app:prod
```

---

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review container logs: `docker logs jira-flask-container`
3. Verify all prerequisites are met
4. Test each step manually before using automation

**Application URL**: http://10.102.99.22:5002

---

## 🎯 Quick Reference

| Command | Description |
|---------|-------------|
| `./docker/build_docker.sh --prod --deploy` | Complete automated deployment |
| `docker ps` | List running containers |
| `docker logs jira-flask-container` | View application logs |
| `curl http://10.102.99.22:5002` | Test application |
| `docker restart jira-flask-container` | Restart application |

---

*Last updated: 2025-06-24*