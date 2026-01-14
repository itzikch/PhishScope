# Quick Start: MCP Server Setup

## 🚀 Get Your MCP Server Running in 10 Minutes

You have your Ubuntu server ready. Here's the fastest way to get started:

---

## Step 1: Copy Installation Script to Your Server

**On your local machine:**

```bash
# Copy the installation script to your server
scp PhishScope/mcp_server_install.sh your-username@your-server-ip:~/

# Example:
scp PhishScope/mcp_server_install.sh ubuntu@192.168.1.100:~/
```

---

## Step 2: Run Installation Script on Server

**SSH into your server:**

```bash
ssh your-username@your-server-ip
```

**Run the installation script:**

```bash
# Make it executable
chmod +x mcp_server_install.sh

# Run it
./mcp_server_install.sh
```

**What it does:**
- ✅ Installs Python 3.11
- ✅ Installs all system dependencies
- ✅ Creates virtual environment
- ✅ Installs MCP SDK and Playwright
- ✅ Installs Chromium browser
- ✅ Tests everything
- ⏱️ Takes about 5-10 minutes

---

## Step 3: Get the MCP Server Code

**I'll provide the MCP server code next. For now, note that you'll need:**

```bash
cd ~/phishscope-mcp
# You'll copy mcp_server.py here (coming in next step)
```

---

## Step 4: Configure

**Edit the .env file:**

```bash
cd ~/phishscope-mcp
nano .env
```

**Add your PhishScope machine IP:**

```bash
# Change this line:
ALLOWED_IPS=192.168.1.50  # Your local machine IP
```

Save and exit (Ctrl+X, Y, Enter)

---

## Step 5: Set Up SSH Key (For Secure Connection)

**On your local machine:**

```bash
# Generate SSH key
ssh-keygen -t ed25519 -f ~/.ssh/phishscope_mcp

# Copy to server
ssh-copy-id -i ~/.ssh/phishscope_mcp.pub your-username@your-server-ip

# Test connection
ssh -i ~/.ssh/phishscope_mcp your-username@your-server-ip
```

---

## Step 6: Configure PhishScope (Your Local Machine)

**Edit PhishScope/.env:**

```bash
cd PhishScope
nano .env
```

**Add these lines:**

```bash
# Enable remote browser
USE_REMOTE_BROWSER=true

# MCP Server connection
MCP_SERVER_TYPE=ssh
MCP_SERVER_HOST=your-server-ip  # e.g., 192.168.1.100
MCP_SERVER_USER=your-username   # e.g., ubuntu
MCP_SERVER_KEY=/home/user/.ssh/phishscope_mcp
MCP_SERVER_PORT=22
```

---

## Step 7: Test Connection

**On your local machine:**

```bash
cd PhishScope

# Test SSH connection
ssh -i ~/.ssh/phishscope_mcp your-username@your-server-ip "echo 'Connection OK'"

# If that works, you're ready!
```

---

## Step 8: Run Your First Analysis

**Once the MCP server code is installed:**

```bash
cd PhishScope
python3 phishscope_cli.py analyze https://example.com
```

**What happens:**
1. PhishScope connects to your Ubuntu server via SSH
2. Server opens the URL in isolated browser
3. Server captures screenshot, DOM, network traffic
4. Results sent back to you
5. Report generated on your machine
6. ✅ Your machine never touched the URL!

---

## 📋 Checklist

Before running analysis, verify:

- [ ] Installation script completed successfully
- [ ] MCP server code copied to ~/phishscope-mcp/
- [ ] .env file configured with your IP
- [ ] SSH key authentication working
- [ ] PhishScope .env configured
- [ ] Can SSH to server without password

---

## 🔧 Troubleshooting

### Can't SSH to server

```bash
# Check if SSH service is running
ssh your-username@your-server-ip
# If it asks for password, SSH key isn't set up correctly
```

### Installation script fails

```bash
# Check system requirements
lsb_release -a  # Should show Ubuntu 22.04
python3.11 --version  # Should show Python 3.11.x
```

### Can't connect from PhishScope

```bash
# Test SSH connection manually
ssh -i ~/.ssh/phishscope_mcp your-username@your-server-ip

# Check server IP is correct
ping your-server-ip
```

---

## 📞 What's Next?

After completing these steps:

1. **I'll provide the MCP server code** (mcp_server.py)
2. **You'll copy it to your server**
3. **Test it works**
4. **Start analyzing malicious URLs safely!**

---

## 🎯 Summary

**Time required:** ~10-15 minutes

**What you get:**
- ✅ Isolated Ubuntu server for malicious URL analysis
- ✅ Secure SSH connection
- ✅ All dependencies installed
- ✅ Ready to receive MCP server code

**Next:** Wait for the MCP server implementation code!

---

**Your server is ready! Let me know when you've completed these steps and I'll provide the MCP server code.**