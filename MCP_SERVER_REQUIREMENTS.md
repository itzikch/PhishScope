# MCP Server Requirements for PhishScope

This document lists everything you need to set up an MCP server for remote browser control with PhishScope.

## 📋 Overview

The MCP server runs in an isolated environment (VM/container) and provides browser automation capabilities to PhishScope via the Model Context Protocol (MCP).

---

## 🖥️ Infrastructure Requirements

### Option 1: Virtual Machine (Recommended for Production)

**Minimum Specifications:**
- **CPU:** 2 cores
- **RAM:** 4 GB
- **Storage:** 20 GB
- **OS:** Ubuntu 22.04 LTS or Debian 12
- **Network:** Isolated network segment (recommended)

**Recommended Specifications:**
- **CPU:** 4 cores
- **RAM:** 8 GB
- **Storage:** 50 GB
- **OS:** Ubuntu 22.04 LTS
- **Network:** Dedicated VLAN with firewall rules

**Cloud Providers:**
- AWS EC2: t3.medium or t3.large
- Azure: Standard_B2s or Standard_B2ms
- GCP: e2-medium or e2-standard-2
- DigitalOcean: 4GB or 8GB Droplet

### Option 2: Docker Container (Recommended for Development)

**Host Requirements:**
- Docker Engine 20.10+
- Docker Compose 2.0+
- 4 GB RAM available
- 10 GB disk space

**Container Specifications:**
```yaml
resources:
  limits:
    cpus: '2'
    memory: 2G
  reservations:
    cpus: '1'
    memory: 1G
```

### Option 3: Kubernetes (Enterprise)

**Cluster Requirements:**
- Kubernetes 1.24+
- 2 CPU cores per pod
- 4 GB RAM per pod
- Network policies enabled
- Pod security policies

---

## 📦 Software Requirements

### 1. Python Environment

**Python Version:**
- Python 3.10 or 3.11 (required)
- Python 3.12 (supported but test first)

**Installation:**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip

# Or use pyenv for version management
curl https://pyenv.run | bash
pyenv install 3.11.7
pyenv global 3.11.7
```

### 2. Python Packages

**Core MCP Packages:**
```txt
# MCP Protocol
mcp>=0.9.0                    # Model Context Protocol SDK
pydantic>=2.0.0               # Data validation
httpx>=0.25.0                 # HTTP client for MCP
```

**Browser Automation:**
```txt
# Playwright
playwright>=1.40.0            # Browser automation
playwright-stealth>=1.0.0     # Anti-detection (optional)
```

**Additional Dependencies:**
```txt
# Utilities
python-dotenv>=1.0.0          # Environment variables
aiofiles>=23.0.0              # Async file operations
pillow>=10.0.0                # Image processing
```

**Complete requirements.txt for MCP Server:**
```txt
# MCP Server Requirements
mcp>=0.9.0
pydantic>=2.0.0
httpx>=0.25.0
playwright>=1.40.0
python-dotenv>=1.0.0
aiofiles>=23.0.0
pillow>=10.0.0
uvicorn>=0.24.0              # If using HTTP transport
fastapi>=0.104.0             # If using HTTP transport
```

### 3. System Dependencies

**Playwright Browser Dependencies:**
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    libatspi2.0-0

# Install Playwright browsers
playwright install chromium
playwright install-deps chromium
```

**For Docker (included in Dockerfile):**
```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget gnupg ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libwayland-client0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxkbcommon0 \
    libxrandr2 \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*
```

---

## 🔐 Security Requirements

### 1. Network Isolation

**Firewall Rules:**
```bash
# Allow only necessary ports
# SSH (if using SSH transport)
sudo ufw allow 22/tcp

# MCP HTTP API (if using HTTP transport)
sudo ufw allow 8080/tcp

# Block all outbound except DNS and specific IPs
sudo ufw default deny outgoing
sudo ufw allow out 53/udp  # DNS
sudo ufw allow out to <your-phishscope-ip>
```

**Network Segmentation:**
- Place MCP server in isolated VLAN
- No direct internet access (use proxy if needed)
- Whitelist only PhishScope client IPs

### 2. User Permissions

**Create dedicated user:**
```bash
# Create non-root user for MCP server
sudo useradd -m -s /bin/bash phishscope-mcp
sudo usermod -aG docker phishscope-mcp  # If using Docker

# Set up SSH key authentication (no passwords)
sudo mkdir -p /home/phishscope-mcp/.ssh
sudo cp authorized_keys /home/phishscope-mcp/.ssh/
sudo chown -R phishscope-mcp:phishscope-mcp /home/phishscope-mcp/.ssh
sudo chmod 700 /home/phishscope-mcp/.ssh
sudo chmod 600 /home/phishscope-mcp/.ssh/authorized_keys
```

### 3. Resource Limits

**System limits (ulimit):**
```bash
# /etc/security/limits.conf
phishscope-mcp soft nofile 1024
phishscope-mcp hard nofile 2048
phishscope-mcp soft nproc 512
phishscope-mcp hard nproc 1024
```

**Docker resource limits:**
```yaml
# docker-compose.yml
services:
  mcp-server:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

---

## 🔌 Connection Requirements

### Option 1: SSH Transport

**Server Side:**
```bash
# Install OpenSSH server
sudo apt install openssh-server

# Configure SSH (recommended settings)
# /etc/ssh/sshd_config
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
AllowUsers phishscope-mcp
```

**Client Side (PhishScope):**
```bash
# Generate SSH key pair
ssh-keygen -t ed25519 -f ~/.ssh/phishscope_mcp -C "phishscope-mcp"

# Copy public key to server
ssh-copy-id -i ~/.ssh/phishscope_mcp.pub phishscope-mcp@mcp-server
```

**Environment Variables:**
```bash
# PhishScope .env
USE_REMOTE_BROWSER=true
MCP_SERVER_TYPE=ssh
MCP_SERVER_HOST=mcp-server.local
MCP_SERVER_USER=phishscope-mcp
MCP_SERVER_KEY=/home/user/.ssh/phishscope_mcp
MCP_SERVER_PORT=22
```

### Option 2: Docker Transport

**Server Side:**
```bash
# Docker daemon must be accessible
# Either via socket or TCP (with TLS)

# Option A: Unix socket (local only)
# Default: /var/run/docker.sock

# Option B: TCP with TLS
# /etc/docker/daemon.json
{
  "hosts": ["tcp://0.0.0.0:2376", "unix:///var/run/docker.sock"],
  "tls": true,
  "tlscert": "/etc/docker/server-cert.pem",
  "tlskey": "/etc/docker/server-key.pem",
  "tlsverify": true,
  "tlscacert": "/etc/docker/ca.pem"
}
```

**Client Side:**
```bash
# PhishScope .env
USE_REMOTE_BROWSER=true
MCP_SERVER_TYPE=docker
MCP_DOCKER_HOST=tcp://mcp-server:2376
MCP_DOCKER_TLS_VERIFY=true
MCP_DOCKER_CERT_PATH=/path/to/certs
MCP_DOCKER_IMAGE=phishscope-mcp:latest
```

### Option 3: HTTP API Transport

**Server Side:**
```bash
# Install additional packages
pip install fastapi uvicorn python-jose[cryptography]

# Run with TLS
uvicorn mcp_server:app \
  --host 0.0.0.0 \
  --port 8443 \
  --ssl-keyfile /path/to/key.pem \
  --ssl-certfile /path/to/cert.pem
```

**Client Side:**
```bash
# PhishScope .env
USE_REMOTE_BROWSER=true
MCP_SERVER_TYPE=http
MCP_SERVER_URL=https://mcp-server.local:8443
MCP_API_KEY=your_secure_api_key_here
MCP_TLS_VERIFY=true
```

---

## 📊 Monitoring Requirements

### 1. Logging

**System Logs:**
```bash
# Configure rsyslog or journald
# /etc/rsyslog.d/phishscope-mcp.conf
:programname, isequal, "mcp-server" /var/log/phishscope-mcp.log
```

**Application Logs:**
```python
# MCP server should log to:
# - /var/log/phishscope-mcp/server.log
# - /var/log/phishscope-mcp/browser.log
# - /var/log/phishscope-mcp/network.log
```

### 2. Metrics

**Recommended Metrics:**
- CPU usage per analysis
- Memory usage per analysis
- Network traffic volume
- Analysis duration
- Success/failure rate
- Browser crashes

**Tools:**
- Prometheus + Grafana (recommended)
- CloudWatch (AWS)
- Azure Monitor (Azure)
- Stackdriver (GCP)

### 3. Alerts

**Alert Conditions:**
- High CPU usage (>80% for 5 min)
- High memory usage (>90%)
- Disk space low (<10%)
- Analysis failures (>10% failure rate)
- Unusual network traffic patterns

---

## 🧪 Testing Requirements

### Pre-Deployment Checklist

**Infrastructure:**
- [ ] VM/container provisioned
- [ ] Network isolation configured
- [ ] Firewall rules applied
- [ ] Resource limits set

**Software:**
- [ ] Python 3.10+ installed
- [ ] All Python packages installed
- [ ] Playwright browsers installed
- [ ] System dependencies installed

**Security:**
- [ ] Non-root user created
- [ ] SSH key authentication configured
- [ ] No password authentication
- [ ] TLS certificates generated (if using HTTPS)

**Connectivity:**
- [ ] Can SSH to server (if using SSH)
- [ ] Can reach Docker daemon (if using Docker)
- [ ] Can reach HTTP API (if using HTTP)
- [ ] Network isolation verified

**Functionality:**
- [ ] MCP server starts without errors
- [ ] Can load test URL
- [ ] Can capture screenshot
- [ ] Can extract DOM
- [ ] Can capture network traffic
- [ ] Browser cleanup works

### Test Commands

```bash
# Test SSH connection
ssh -i ~/.ssh/phishscope_mcp phishscope-mcp@mcp-server "echo 'Connection OK'"

# Test Python environment
ssh phishscope-mcp@mcp-server "python3 --version && pip list"

# Test Playwright
ssh phishscope-mcp@mcp-server "playwright --version"

# Test browser launch
ssh phishscope-mcp@mcp-server "python3 -c 'from playwright.sync_api import sync_playwright; p = sync_playwright().start(); browser = p.chromium.launch(); print(\"Browser OK\"); browser.close()'"
```

---

## 💰 Cost Estimates

### Cloud VM (Monthly)

**AWS EC2:**
- t3.medium (2 vCPU, 4GB): ~$30/month
- t3.large (2 vCPU, 8GB): ~$60/month

**Azure:**
- Standard_B2s (2 vCPU, 4GB): ~$30/month
- Standard_B2ms (2 vCPU, 8GB): ~$60/month

**GCP:**
- e2-medium (2 vCPU, 4GB): ~$25/month
- e2-standard-2 (2 vCPU, 8GB): ~$50/month

**DigitalOcean:**
- 4GB Droplet: $24/month
- 8GB Droplet: $48/month

### On-Premise

**Hardware:**
- Dedicated server: $500-2000 (one-time)
- Electricity: ~$10-20/month
- Maintenance: Variable

### Docker (Local)

**Cost:** Free (uses existing infrastructure)
**Resource Impact:** Moderate

---

## 📚 Documentation Needed

Before deploying, prepare:

1. **Network Diagram** - Show MCP server placement
2. **Firewall Rules** - Document all allowed connections
3. **SSH Keys** - Securely store and document key locations
4. **API Keys** - If using HTTP transport
5. **Runbook** - Deployment and troubleshooting procedures
6. **Disaster Recovery** - Backup and restore procedures

---

## 🚀 Quick Start Summary

**Minimum to Get Started:**

1. **Infrastructure:** Ubuntu 22.04 VM with 4GB RAM
2. **Software:** Python 3.11 + Playwright
3. **Packages:** `pip install mcp playwright python-dotenv`
4. **Browser:** `playwright install chromium`
5. **Connection:** SSH with key authentication
6. **Security:** Firewall + isolated network

**Estimated Setup Time:**
- Basic setup: 1-2 hours
- Production-ready: 4-8 hours
- Enterprise deployment: 1-2 days

---

## ❓ Next Steps

Once you have these requirements ready, you can:

1. Provision the infrastructure
2. Install the software
3. Request the MCP server implementation
4. Deploy and test
5. Integrate with PhishScope

Would you like me to create the actual MCP server implementation once you have the infrastructure ready?