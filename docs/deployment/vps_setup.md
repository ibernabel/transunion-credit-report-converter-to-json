# VPS Setup Guide - TransUnion PDF to JSON API

Complete guide for deploying the TransUnion PDF to JSON API service on a VPS.

---

## System Requirements

### Minimum Hardware Requirements

- **CPU**: 1 vCPU/Core
- **RAM**: 2GB
- **Storage**: 20GB SSD
- **Network**: 1GB/month bandwidth

### Recommended Hardware Requirements

- **CPU**: 2 vCPU/Cores
- **RAM**: 4GB
- **Storage**: 40GB SSD
- **Network**: 2GB/month bandwidth

### Operating System

- Ubuntu 22.04 LTS or newer (recommended)
- Ubuntu 20.04 LTS
- Debian 11 or newer

---

## Initial Server Setup

### 1. Update System Packages

```bash
# Update package lists and upgrade installed packages
sudo apt update
sudo apt upgrade -y
```

### 2. Create Non-root User

```bash
# Create deployment user
sudo adduser deploy

# Add user to sudo group
sudo usermod -aG sudo deploy
```

### 3. Configure SSH Security

```bash
# Edit SSH configuration
sudo nano /etc/ssh/sshd_config

# Set these values for security
PermitRootLogin no
PasswordAuthentication no
Port 2222  # Change default SSH port (optional but recommended)

# Restart SSH service
sudo systemctl restart sshd
```

**⚠️ Important**: If you change the SSH port, make note of it before logging out!

### 4. Configure Firewall (UFW)

```bash
# Install UFW if not present
sudo apt install ufw

# Allow SSH (use your custom port if changed)
sudo ufw allow 2222/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow the API port (if exposing directly)
sudo ufw allow 8000/tcp

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

---

## Docker Installation

### Install Docker and Docker Compose

```bash
# Add Docker's official GPG key
sudo apt update
sudo apt install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Add Docker repository
echo \
  "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker packages
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Add user to docker group
sudo usermod -aG docker $USER
sudo usermod -aG docker deploy

# Logout and login again for group changes to take effect
```

### Verify Docker Installation

```bash
# Test Docker installation
docker --version
docker compose version

# Run test container
docker run hello-world
```

---

## Security Hardening

### 1. Enable Automatic Security Updates

```bash
# Install unattended-upgrades
sudo apt install unattended-upgrades

# Configure automatic updates
sudo dpkg-reconfigure -plow unattended-upgrades
```

### 2. Install and Configure Fail2ban

```bash
# Install Fail2ban
sudo apt install fail2ban

# Copy configuration
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local

# Enable and start service
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# Check status
sudo fail2ban-client status
```

### 3. Configure System Limits

```bash
# Edit system limits
sudo nano /etc/security/limits.conf

# Add these lines
*          soft    nofile      65535
*          hard    nofile      65535
```

### 4. Docker Security

**Use Official Images Only**: Our Dockerfile uses `python:3.12-slim` from Docker Hub.

**Regular Security Scans**:

```bash
# Install Trivy for container scanning
sudo apt install -y wget apt-transport-https gnupg lsb-release
wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | sudo apt-key add -
echo "deb https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main" | sudo tee -a /etc/apt/sources.list.d/trivy.list
sudo apt update
sudo apt install trivy

# Scan Docker image
trivy image transunion-parser:1.0.0
```

---

## Application Deployment

### 1. Create Application Directory

```bash
# Create directory structure
sudo mkdir -p /opt/transunion-parser
sudo chown -R deploy:deploy /opt/transunion-parser
cd /opt/transunion-parser
```

### 2. Clone Repository

```bash
# Clone the repository (replace with your repository URL)
git clone https://github.com/your-username/transunion-pdf-to-json.git .

# Or if using SSH
git clone git@github.com:your-username/transunion-pdf-to-json.git .
```

### 3. Configure Environment Variables (Optional)

```bash
# Create environment file for custom configuration
nano .env

# Add environment variables (examples)
DEBUG=0
MAX_WORKERS=4
LOG_LEVEL=info
MAX_LOG_SIZE_MB=100
BACKUP_RETENTION_DAYS=7
```

### 4. Build and Deploy

```bash
# Build the Docker image
docker build -t transunion-parser:1.0.0 .

# Start services using production compose file
docker compose -f docker-compose.prod.yml up -d

# Check logs
docker compose -f docker-compose.prod.yml logs -f
```

### 5. Verify Deployment

```bash
# Check if container is running
docker ps

# Test health endpoint
curl http://localhost:8000/v1/health

# Expected response: {"status": "healthy"}
```

---

## Monitoring and Logging

### Application Logging

The application uses structured JSON logging:

```bash
# View API logs
tail -f logs/api.log

# View monitoring logs (system metrics)
tail -f logs/monitoring.log

# View Docker container logs
docker compose -f docker-compose.prod.yml logs -f
```

### Log Files

| Log File              | Purpose                            | Rotation |
| --------------------- | ---------------------------------- | -------- |
| `logs/api.log`        | API requests, responses, errors    | 100MB    |
| `logs/monitoring.log` | System metrics (CPU, memory, disk) | 100MB    |

### System Metrics Monitoring

Built-in metrics logged every 60 seconds:

- CPU usage percentage
- Memory utilization
- Disk usage
- Request/response timing
- Error tracking

### View Metrics

```bash
# View latest metrics
tail -n 50 logs/monitoring.log | jq '.'

# Monitor in real-time (requires jq)
tail -f logs/monitoring.log | jq '.'

# Install monitoring tools
sudo apt install -y htop iotop nethogs

# Monitor system resources
htop
```

---

## Backup and Maintenance

### Automated Backup System

The application includes built-in automated backups:

- **Daily backups** at 2:00 AM
- **7-day retention** policy
- **Automatic log rotation** when files exceed 100MB
- **Compressed archives** (tar.gz format)

### Set Up Automated Maintenance

```bash
# Make maintenance script executable
chmod +x /opt/transunion-parser/src/maintenance.py

# Set up cron job for maintenance
crontab -e

# Add this line to run maintenance at 2 AM daily
0 2 * * * cd /opt/transunion-parser && /usr/bin/python3 src/maintenance.py >> logs/cron.log 2>&1
```

### Manual Backup Operations

```bash
# Trigger manual backup
cd /opt/transunion-parser
python3 -c "from src.utils.backup import BackupManager; BackupManager().create_backup()"

# View backup logs
tail -f logs/api.log | grep backup

# List backups
ls -lh backups/

# View backup size
du -sh backups/*
```

### Restore from Backup

```bash
# Navigate to application directory
cd /opt/transunion-parser

# Extract backup
tar -xzf backups/backup_YYYYMMDD_HHMMSS.tar.gz

# Restart services if needed
docker compose -f docker-compose.prod.yml restart
```

---

## SSL/TLS Setup (with Nginx Reverse Proxy)

### Install Nginx

```bash
# Install Nginx
sudo apt install nginx

# Start and enable Nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

### Configure Nginx Reverse Proxy

```bash
# Create Nginx configuration
sudo nano /etc/nginx/sites-available/transunion-parser

# Add this configuration:
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Enable site
sudo ln -s /etc/nginx/sites-available/transunion-parser /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

### Install SSL with Certbot

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com

# Certbot will automatically configure Nginx for HTTPS
```

---

## Troubleshooting

### Common Commands

```bash
# Check container status
docker ps
docker compose -f docker-compose.prod.yml ps

# View container logs
docker compose -f docker-compose.prod.yml logs -f

# Restart services
docker compose -f docker-compose.prod.yml restart

# Stop services
docker compose -f docker-compose.prod.yml down

# Rebuild and restart
docker compose -f docker-compose.prod.yml up -d --build
```

### Check System Resources

```bash
# Disk space
df -h

# Memory usage
free -m

# CPU usage
top
# Or better: htop

# Docker disk usage
docker system df

# Clean up Docker
docker system prune -a
```

### Log Locations

| Type         | Location                                     | Purpose        |
| ------------ | -------------------------------------------- | -------------- |
| Application  | `/opt/transunion-parser/logs/api.log`        | API logs       |
| Monitoring   | `/opt/transunion-parser/logs/monitoring.log` | Metrics        |
| System       | `/var/log/syslog`                            | System logs    |
| Nginx        | `/var/log/nginx/access.log`                  | HTTP access    |
| Nginx Errors | `/var/log/nginx/error.log`                   | HTTP errors    |
| Docker       | `docker compose logs`                        | Container logs |

### Common Issues

**Issue**: Container won't start

```bash
# Check logs
docker compose -f docker-compose.prod.yml logs

# Check if port is already in use
sudo lsof -i :8000

# Kill process using port
sudo kill -9 <PID>
```

**Issue**: High memory usage

```bash
# Check container resource usage
docker stats

# Adjust resource limits in docker-compose.prod.yml
```

**Issue**: Disk full

```bash
# Clean up Docker
docker system prune -a

# Clean up old backups manually
rm backups/backup_old*.tar.gz

# Check log sizes
du -sh logs/*
```

---

## Maintenance Procedures

### Regular Maintenance Tasks

| Task                    | Frequency    | Automated                       |
| ----------------------- | ------------ | ------------------------------- |
| System packages update  | Weekly       | Manual                          |
| Security updates        | Daily        | Automatic (unattended-upgrades) |
| Monitor disk usage      | Daily        | Automatic (logs)                |
| Rotate logs             | As needed    | Automatic (>100MB)              |
| Create backups          | Daily        | Automatic (2 AM)                |
| Clean old backups       | Daily        | Automatic (>7 days)             |
| Update SSL certificates | Auto-renewal | Automatic (Certbot)             |
| Review error logs       | Weekly       | Manual                          |
| Security audit          | Monthly      | Manual                          |

### Manual Updates

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Pull latest code
cd /opt/transunion-parser
git pull origin main

# Rebuild and restart
docker compose -f docker-compose.prod.yml up -d --build

# Verify
curl http://localhost:8000/v1/health
```

---

## Scaling Considerations

### Vertical Scaling (Increase Resources)

1. Upgrade VPS plan
2. Adjust worker count in `docker-compose.prod.yml`
3. Increase resource limits

### Horizontal Scaling (Multiple Instances)

1. Set up load balancer (Nginx, HAProxy)
2. Deploy multiple instances on different ports
3. Configure load balancer to distribute traffic

### Performance Optimization

```yaml
# docker-compose.prod.yml adjustments
services:
  api:
    deploy:
      resources:
        limits:
          cpus: "2.0"
          memory: 2G
        reservations:
          cpus: "1.0"
          memory: 1G
```

---

## Support

For issues or questions:

1. Check logs: `logs/api.log`
2. Review this documentation
3. Check GitHub issues
4. Review error patterns in monitoring logs

---

**🎉 Deployment Complete!**

Your API should now be accessible at:

- Local: `http://localhost:8000`
- With Nginx: `http://your-domain.com`
- With SSL: `https://your-domain.com`

API Documentation: `https://your-domain.com/docs`
