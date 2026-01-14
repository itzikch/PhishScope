# MCP Server Setup Guide - Ubuntu Server

## 🚀 Quick Start

You have your Ubuntu server ready! Follow these steps to set up the MCP server for PhishScope.

---

## 📋 Step-by-Step Installation

### Step 1: Connect to Your Ubuntu Server

```bash
# From your local machine
ssh your-username@your-server-ip

# Example:
ssh ubuntu@192.168.1.100
```

### Step 2: Update System

```bash
# Update package lists
sudo apt update && sudo apt upgrade -y
```

### Step 3: Install Python 3.11

```bash
# Install Python 3.11
sudo apt install -y python3.11 python3.11-venv python3-pip

# Verify installation
python3.11 --version
# Should show: Python 3.11.x
```

### Step 4: Install System Dependencies

```bash
# Install required system packages
sudo apt install -y \
    wget \
    gnupg \
    ca-certificates \
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
    xdg-utils
```

### Step 5: Create Dedicated User

```bash
# Create user for MCP server
sudo useradd -m -s /bin/bash phishscope-mcp

# Set password (optional, for sudo access)
sudo passwd phishscope-mcp

# Switch to the new user
sudo su - phishscope-mcp
```

### Step 6: Download MCP Server Files

```bash
# Create directory structure
mkdir -p ~/phishscope-mcp
cd ~/phishscope-mcp

# You'll copy the MCP server files here
# (We'll create them in the next steps)
```

### Step 7: Set Up Python Environment

```bash
# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

### Step 8: Install Python Packages

```bash
# Install required packages
pip install \
    mcp>=0.9.0 \
    playwright>=1.40.0 \
    python-dotenv>=1.0.0 \
    aiofiles>=23.0.0 \
    pillow>=10.0.0 \
    pydantic>=2.0.0 \
    httpx>=0.25.0

# Install Playwright browsers
playwright install chromium

# Install Playwright system dependencies
playwright install-deps chromium
```

### Step 9: Configure Firewall (Optional but Recommended)

```bash
# Exit from phishscope-mcp user
exit

# Configure UFW firewall
sudo ufw allow 22/tcp  # SSH
sudo ufw enable

# Check status
sudo ufw status
```

### Step 10: Set Up SSH Key Authentication

**On your local machine:**

```bash
# Generate SSH key pair (if you don't have one)
ssh-keygen -t ed25519 -f ~/.ssh/phishscope_mcp -C "phishscope-mcp"

# Copy public key to server
ssh-copy-id -i ~/.ssh/phishscope_mcp.pub phishscope-mcp@your-server-ip

# Test connection
ssh -i ~/.ssh/phishscope_mcp phishscope-mcp@your-server-ip
```

---

## 📦 Install MCP Server Code

### Option A: Manual Installation

**1. Create the MCP server file on your Ubuntu server:**

```bash
# As phishscope-mcp user
cd ~/phishscope-mcp
nano mcp_server.py
```

**2. Copy the MCP server code** (I'll provide this in the next file)

**3. Create requirements file:**

```bash
nano requirements.txt
```

Add:
```txt
mcp>=0.9.0
playwright>=1.40.0
python-dotenv>=1.0.0
aiofiles>=23.0.0
pillow>=10.0.0
pydantic>=2.0.0
httpx>=0.25.0
```

**4. Install:**

```bash
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

### Option B: Automated Installation Script

**Run this on your Ubuntu server:**

```bash
# Download and run setup script
wget https://raw.githubusercontent.com/your-repo/phishscope/main/mcp_server/install.sh
chmod +x install.sh
./install.sh
```

---

## 🧪 Test the Installation

### Test 1: Python Environment

```bash
# Activate venv
source ~/phishscope-mcp/venv/bin/activate

# Test Python
python --version
# Should show: Python 3.11.x

# Test imports
python -c "import playwright; print('Playwright OK')"
python -c "import mcp; print('MCP OK')"
```

### Test 2: Playwright Browser

```bash
# Test browser launch
python -c "
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch()
    print('Browser launched successfully!')
    browser.close()
"
```

### Test 3: MCP Server

```bash
# Test MCP server (we'll add this after creating the server code)
python mcp_server.py --test
```

---

## 🔧 Configuration

### Create .env file

```bash
cd ~/phishscope-mcp
nano .env
```

Add:
```bash
# MCP Server Configuration
MCP_SERVER_PORT=8080
MCP_LOG_LEVEL=INFO
MCP_MAX_CONCURRENT=5

# Browser Configuration
BROWSER_HEADLESS=true
BROWSER_TIMEOUT=30000

# Security
ALLOWED_IPS=192.168.1.50  # Your PhishScope machine IP
```

---

## 🔒 Security Hardening

### 1. Disable Password Authentication

```bash
# Edit SSH config
sudo nano /etc/ssh/sshd_config
```

Set:
```
PasswordAuthentication no
PubkeyAuthentication yes
PermitRootLogin no
```

Restart SSH:
```bash
sudo systemctl restart sshd
```

### 2. Set Resource Limits

```bash
# Edit limits
sudo nano /etc/security/limits.conf
```

Add:
```
phishscope-mcp soft nofile 1024
phishscope-mcp hard nofile 2048
phishscope-mcp soft nproc 512
phishscope-mcp hard nproc 1024
```

### 3. Network Isolation (Optional)

```bash
# Block all outbound except specific IPs
sudo ufw default deny outgoing
sudo ufw allow out 53/udp  # DNS
sudo ufw allow out to 192.168.1.50  # Your PhishScope machine
```

---

## 🚀 Start the MCP Server

### Manual Start

```bash
cd ~/phishscope-mcp
source venv/bin/activate
python mcp_server.py
```

### As a Service (Recommended)

**Create systemd service:**

```bash
sudo nano /etc/systemd/system/phishscope-mcp.service
```

Add:
```ini
[Unit]
Description=PhishScope MCP Server
After=network.target

[Service]
Type=simple
User=phishscope-mcp
WorkingDirectory=/home/phishscope-mcp/phishscope-mcp
Environment="PATH=/home/phishscope-mcp/phishscope-mcp/venv/bin"
ExecStart=/home/phishscope-mcp/phishscope-mcp/venv/bin/python mcp_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable and start:**

```bash
sudo systemctl daemon-reload
sudo systemctl enable phishscope-mcp
sudo systemctl start phishscope-mcp

# Check status
sudo systemctl status phishscope-mcp

# View logs
sudo journalctl -u phishscope-mcp -f
```

---

## 📊 Monitoring

### Check Logs

```bash
# Real-time logs
sudo journalctl -u phishscope-mcp -f

# Last 100 lines
sudo journalctl -u phishscope-mcp -n 100

# Logs from today
sudo journalctl -u phishscope-mcp --since today
```

### Check Resource Usage

```bash
# CPU and memory
top -u phishscope-mcp

# Disk usage
df -h

# Network connections
sudo netstat -tulpn | grep python
```

---

## 🔧 Troubleshooting

### Issue: Playwright browser won't start

**Solution:**
```bash
# Reinstall browser dependencies
source ~/phishscope-mcp/venv/bin/activate
playwright install-deps chromium
```

### Issue: Permission denied

**Solution:**
```bash
# Fix permissions
sudo chown -R phishscope-mcp:phishscope-mcp ~/phishscope-mcp
chmod +x ~/phishscope-mcp/mcp_server.py
```

### Issue: Can't connect from PhishScope

**Solution:**
```bash
# Check firewall
sudo ufw status

# Check if server is running
sudo systemctl status phishscope-mcp

# Check if port is listening
sudo netstat -tulpn | grep 8080
```

### Issue: Out of memory

**Solution:**
```bash
# Check memory
free -h

# Reduce concurrent analyses in .env
MCP_MAX_CONCURRENT=2
```

---

## ✅ Verification Checklist

Before connecting PhishScope, verify:

- [ ] Python 3.11 installed
- [ ] All system dependencies installed
- [ ] Virtual environment created and activated
- [ ] All Python packages installed
- [ ] Playwright browser installed
- [ ] SSH key authentication working
- [ ] Firewall configured
- [ ] MCP server starts without errors
- [ ] Can launch browser successfully
- [ ] Service running (if using systemd)

---

## 🎯 Next Steps

Once your server is set up:

1. **Configure PhishScope** (on your local machine):
   ```bash
   # Edit PhishScope/.env
   USE_REMOTE_BROWSER=true
   MCP_SERVER_TYPE=ssh
   MCP_SERVER_HOST=your-server-ip
   MCP_SERVER_USER=phishscope-mcp
   MCP_SERVER_KEY=/path/to/phishscope_mcp
   ```

2. **Test connection**:
   ```bash
   cd PhishScope
   python3 test_mcp_connection.py
   ```

3. **Run your first analysis**:
   ```bash
   python3 phishscope_cli.py analyze https://example.com
   ```

---

## 📞 Support

If you encounter issues:

1. Check the logs: `sudo journalctl -u phishscope-mcp -f`
2. Verify all dependencies are installed
3. Test SSH connection manually
4. Check firewall rules
5. Review the troubleshooting section above

---

**Your Ubuntu server is now ready for the MCP server installation!**

Next, I'll provide the actual MCP server code to install.