#!/bin/bash
#
# PhishScope MCP Server Installation Script
# For Ubuntu 22.04 LTS
#
# Usage: ./mcp_server_install.sh
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

print_header() {
    echo ""
    echo "=================================="
    echo "$1"
    echo "=================================="
    echo ""
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    print_error "Please do not run as root. Run as a regular user with sudo privileges."
    exit 1
fi

print_header "PhishScope MCP Server Installation"

# Step 1: Update system
print_info "Updating system packages..."
sudo apt update && sudo apt upgrade -y
print_success "System updated"

# Step 2: Install Python 3.11
print_info "Installing Python 3.11..."
sudo apt install -y python3.11 python3.11-venv python3-pip
PYTHON_VERSION=$(python3.11 --version)
print_success "Python installed: $PYTHON_VERSION"

# Step 3: Install system dependencies
print_info "Installing system dependencies..."
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
print_success "System dependencies installed"

# Step 4: Create directory structure
print_info "Creating directory structure..."
mkdir -p ~/phishscope-mcp
cd ~/phishscope-mcp
print_success "Directory created: ~/phishscope-mcp"

# Step 5: Create Python virtual environment
print_info "Creating Python virtual environment..."
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
print_success "Virtual environment created"

# Step 6: Create requirements.txt
print_info "Creating requirements.txt..."
cat > requirements.txt << 'EOF'
# MCP Server Requirements
mcp>=0.9.0
playwright>=1.40.0
python-dotenv>=1.0.0
aiofiles>=23.0.0
pillow>=10.0.0
pydantic>=2.0.0
httpx>=0.25.0
EOF
print_success "requirements.txt created"

# Step 7: Install Python packages
print_info "Installing Python packages (this may take a few minutes)..."
pip install -r requirements.txt
print_success "Python packages installed"

# Step 8: Install Playwright browsers
print_info "Installing Playwright Chromium browser..."
playwright install chromium
print_success "Chromium browser installed"

# Step 9: Install Playwright system dependencies
print_info "Installing Playwright system dependencies..."
playwright install-deps chromium
print_success "Playwright dependencies installed"

# Step 10: Create .env file
print_info "Creating .env configuration file..."
cat > .env << 'EOF'
# MCP Server Configuration
MCP_SERVER_PORT=8080
MCP_LOG_LEVEL=INFO
MCP_MAX_CONCURRENT=5

# Browser Configuration
BROWSER_HEADLESS=true
BROWSER_TIMEOUT=30000

# Security
# Add your PhishScope machine IP here
ALLOWED_IPS=
EOF
print_success ".env file created"

# Step 11: Test installation
print_info "Testing installation..."

# Test Python
python --version > /dev/null 2>&1 && print_success "Python OK" || print_error "Python test failed"

# Test imports
python -c "import playwright" > /dev/null 2>&1 && print_success "Playwright import OK" || print_error "Playwright import failed"
python -c "import mcp" > /dev/null 2>&1 && print_success "MCP import OK" || print_error "MCP import failed"

# Test browser launch
print_info "Testing browser launch..."
python -c "
from playwright.sync_api import sync_playwright
try:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        browser.close()
    print('Browser test: OK')
except Exception as e:
    print(f'Browser test: FAILED - {e}')
    exit(1)
" && print_success "Browser launch OK" || print_error "Browser launch failed"

# Step 12: Create start script
print_info "Creating start script..."
cat > start_mcp_server.sh << 'EOF'
#!/bin/bash
cd ~/phishscope-mcp
source venv/bin/activate
python mcp_server.py
EOF
chmod +x start_mcp_server.sh
print_success "Start script created: start_mcp_server.sh"

# Step 13: Create systemd service file template
print_info "Creating systemd service template..."
cat > phishscope-mcp.service << EOF
[Unit]
Description=PhishScope MCP Server
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$HOME/phishscope-mcp
Environment="PATH=$HOME/phishscope-mcp/venv/bin"
ExecStart=$HOME/phishscope-mcp/venv/bin/python mcp_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
print_success "Systemd service template created"

# Final summary
print_header "Installation Complete!"

echo "📁 Installation directory: ~/phishscope-mcp"
echo ""
echo "✅ Installed components:"
echo "   - Python 3.11"
echo "   - Virtual environment"
echo "   - MCP SDK"
echo "   - Playwright + Chromium"
echo "   - All dependencies"
echo ""
echo "📋 Next steps:"
echo ""
echo "1. Download the MCP server code:"
echo "   cd ~/phishscope-mcp"
echo "   # Copy mcp_server.py to this directory"
echo ""
echo "2. Edit .env file to add your PhishScope machine IP:"
echo "   nano .env"
echo "   # Set ALLOWED_IPS=your.phishscope.ip"
echo ""
echo "3. Test the MCP server:"
echo "   source venv/bin/activate"
echo "   python mcp_server.py --test"
echo ""
echo "4. (Optional) Install as systemd service:"
echo "   sudo cp phishscope-mcp.service /etc/systemd/system/"
echo "   sudo systemctl daemon-reload"
echo "   sudo systemctl enable phishscope-mcp"
echo "   sudo systemctl start phishscope-mcp"
echo ""
echo "5. Configure PhishScope on your local machine:"
echo "   Edit PhishScope/.env:"
echo "   USE_REMOTE_BROWSER=true"
echo "   MCP_SERVER_HOST=$(hostname -I | awk '{print $1}')"
echo ""
print_success "Installation script completed successfully!"
echo ""
echo "Server IP: $(hostname -I | awk '{print $1}')"
echo "Installation path: ~/phishscope-mcp"
echo ""

# Made with Bob
