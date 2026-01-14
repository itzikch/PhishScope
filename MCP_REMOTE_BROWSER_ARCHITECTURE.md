# MCP Remote Browser Architecture for PhishScope

## Overview

This document explains how PhishScope can use MCP (Model Context Protocol) to control a remote browser in an isolated environment for safe analysis of malicious URLs.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Your Local Machine                           │
│  ┌────────────────────────────────────────────────────────┐    │
│  │              PhishScope Client                          │    │
│  │  - CLI / Web Interface                                  │    │
│  │  - Analysis Orchestration                               │    │
│  │  - Report Generation                                    │    │
│  └────────────────┬───────────────────────────────────────┘    │
│                   │ MCP Protocol (JSON-RPC over stdio/HTTP)     │
└───────────────────┼─────────────────────────────────────────────┘
                    │
                    │ Secure Connection
                    │
┌───────────────────▼─────────────────────────────────────────────┐
│              Isolated VM / Container                             │
│  ┌────────────────────────────────────────────────────────┐    │
│  │           PhishScope MCP Server                         │    │
│  │  - Exposes browser control tools via MCP               │    │
│  │  - Manages Playwright browser instances                │    │
│  │  - Handles page loading, screenshots, DOM extraction   │    │
│  │  - Network traffic capture                             │    │
│  └────────────────┬───────────────────────────────────────┘    │
│                   │                                              │
│  ┌────────────────▼───────────────────────────────────────┐    │
│  │         Playwright Browser (Chromium)                   │    │
│  │  - Loads malicious URLs                                 │    │
│  │  - Executes JavaScript                                  │    │
│  │  - Captures screenshots                                 │    │
│  │  - Records network traffic                              │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  Network: Isolated / Monitored                                  │
│  Storage: Ephemeral (destroyed after analysis)                  │
└──────────────────────────────────────────────────────────────────┘
```

## 🔧 How It Works

### 1. **MCP Server (Remote Side)**

The MCP server runs in an isolated environment and exposes browser control capabilities:

**Tools Exposed:**
- `load_page` - Load a URL in the browser
- `take_screenshot` - Capture page screenshot
- `get_dom` - Extract DOM structure
- `get_network_log` - Get network traffic
- `execute_javascript` - Run JS in page context
- `cleanup` - Destroy browser instance

**Example MCP Server Implementation:**
```python
# mcp_server/browser_server.py
from mcp.server import Server
from playwright.async_api import async_playwright

class BrowserMCPServer(Server):
    def __init__(self):
        super().__init__("phishscope-browser")
        self.browser = None
        self.page = None
        
    @self.tool()
    async def load_page(self, url: str) -> dict:
        """Load a URL in isolated browser"""
        async with async_playwright() as p:
            self.browser = await p.chromium.launch(headless=True)
            self.page = await self.browser.new_page()
            
            # Capture network traffic
            network_log = []
            self.page.on("request", lambda req: network_log.append({
                "url": req.url,
                "method": req.method
            }))
            
            # Load page
            response = await self.page.goto(url, wait_until="networkidle")
            
            return {
                "success": True,
                "url": url,
                "status": response.status,
                "title": await self.page.title(),
                "network_requests": len(network_log)
            }
    
    @self.tool()
    async def take_screenshot(self) -> str:
        """Capture screenshot and return base64"""
        screenshot = await self.page.screenshot()
        return base64.b64encode(screenshot).decode()
    
    @self.tool()
    async def get_dom(self) -> str:
        """Extract DOM HTML"""
        return await self.page.content()
    
    @self.tool()
    async def cleanup(self):
        """Destroy browser instance"""
        if self.browser:
            await self.browser.close()
        return {"success": True}
```

### 2. **PhishScope Client (Local Side)**

PhishScope connects to the MCP server and uses its tools:

**Modified PageLoaderAgent:**
```python
# agents/page_loader_remote.py
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class RemotePageLoaderAgent:
    def __init__(self, logger, mcp_server_command):
        self.logger = logger
        self.mcp_command = mcp_server_command
        
    async def load_page(self, url: str, output_dir: Path) -> dict:
        """Load page using remote MCP server"""
        
        # Connect to MCP server
        server_params = StdioServerParameters(
            command=self.mcp_command,  # e.g., "ssh user@vm python mcp_server.py"
            args=[],
            env=None
        )
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                # Call remote load_page tool
                result = await session.call_tool(
                    "load_page",
                    arguments={"url": url}
                )
                
                # Get screenshot
                screenshot_b64 = await session.call_tool(
                    "take_screenshot",
                    arguments={}
                )
                
                # Save screenshot locally
                screenshot_path = output_dir / "screenshot.png"
                screenshot_data = base64.b64decode(screenshot_b64)
                screenshot_path.write_bytes(screenshot_data)
                
                # Get DOM
                dom_html = await session.call_tool(
                    "get_dom",
                    arguments={}
                )
                
                # Cleanup remote browser
                await session.call_tool("cleanup", arguments={})
                
                return {
                    "success": True,
                    "url": url,
                    "screenshot_path": str(screenshot_path),
                    "dom_html": dom_html,
                    **result
                }
```

### 3. **Configuration**

**Environment Variables:**
```bash
# .env
# Enable remote browser mode
USE_REMOTE_BROWSER=true

# MCP server connection
MCP_SERVER_TYPE=ssh  # or 'docker', 'http'
MCP_SERVER_HOST=analysis-vm.example.com
MCP_SERVER_USER=phishscope
MCP_SERVER_KEY=/path/to/ssh/key

# Or for Docker
MCP_DOCKER_IMAGE=phishscope-browser:latest
MCP_DOCKER_NETWORK=isolated

# Or for HTTP
MCP_SERVER_URL=https://browser-api.example.com
MCP_API_KEY=your_api_key
```

## 🔒 Security Benefits

### 1. **Complete Isolation**
- Malicious code runs in separate VM/container
- No access to your local filesystem
- No access to your local network
- Can be destroyed after each analysis

### 2. **Network Monitoring**
- All traffic goes through isolated network
- Can log/block suspicious connections
- Prevent data exfiltration to attacker

### 3. **Resource Limits**
- CPU/memory limits on remote environment
- Prevent resource exhaustion attacks
- Automatic timeout and cleanup

### 4. **Audit Trail**
- All browser actions logged via MCP
- Complete record of what was executed
- Forensic evidence preserved

## 🚀 Deployment Options

### Option 1: SSH to Remote VM
```bash
# Start MCP server on remote VM
ssh user@analysis-vm "python3 /opt/phishscope/mcp_server.py"

# PhishScope connects via SSH tunnel
MCP_SERVER_TYPE=ssh
MCP_SERVER_HOST=analysis-vm
```

### Option 2: Docker Container
```bash
# Run MCP server in container
docker run -d --name phishscope-browser \
  --network isolated \
  --memory 2g \
  --cpus 1 \
  phishscope-browser:latest

# PhishScope connects to container
MCP_SERVER_TYPE=docker
MCP_DOCKER_CONTAINER=phishscope-browser
```

### Option 3: HTTP API
```bash
# MCP server exposed via HTTP
# (with authentication and rate limiting)
MCP_SERVER_TYPE=http
MCP_SERVER_URL=https://browser-api.internal
MCP_API_KEY=secret_key
```

### Option 4: Cloud VM (AWS/Azure/GCP)
```bash
# Spin up ephemeral VM for each analysis
# Destroy after completion
# Use cloud provider's isolation features
```

## 📊 Performance Considerations

### Latency
- **Local Browser:** ~2-5 seconds per analysis
- **Remote Browser (LAN):** ~3-7 seconds per analysis
- **Remote Browser (Cloud):** ~5-15 seconds per analysis

### Throughput
- **Single Remote Server:** 10-20 analyses/minute
- **Load Balanced Pool:** 100+ analyses/minute
- **Auto-scaling:** Unlimited (cost-dependent)

## 🛠️ Implementation Plan

### Phase 1: Basic MCP Server (Week 1)
- [ ] Create MCP server with browser tools
- [ ] Implement load_page, screenshot, get_dom
- [ ] Add network traffic capture
- [ ] Test with local MCP connection

### Phase 2: Remote Connection (Week 2)
- [ ] Add SSH transport support
- [ ] Add Docker transport support
- [ ] Implement authentication
- [ ] Add connection pooling

### Phase 3: Production Features (Week 3)
- [ ] Add HTTP API transport
- [ ] Implement rate limiting
- [ ] Add monitoring and logging
- [ ] Create deployment scripts

### Phase 4: Advanced Features (Week 4)
- [ ] Auto-scaling support
- [ ] Multi-region deployment
- [ ] Advanced network isolation
- [ ] Forensic evidence collection

## 🔍 Example Usage

### Basic Remote Analysis
```bash
# Configure remote browser
export USE_REMOTE_BROWSER=true
export MCP_SERVER_HOST=analysis-vm.local

# Run analysis (browser runs remotely)
python3 phishscope_cli.py analyze https://malicious-site.com

# Results returned to local machine
# Remote browser destroyed automatically
```

### Web Interface
```python
# Web app automatically uses remote browser
# Users don't need to know about MCP
# Transparent isolation
```

## 📝 Configuration Examples

### Development (Local Docker)
```env
USE_REMOTE_BROWSER=true
MCP_SERVER_TYPE=docker
MCP_DOCKER_IMAGE=phishscope-browser:dev
MCP_DOCKER_NETWORK=phishscope-isolated
```

### Production (Cloud VM Pool)
```env
USE_REMOTE_BROWSER=true
MCP_SERVER_TYPE=http
MCP_SERVER_URL=https://browser-pool.internal
MCP_API_KEY=${BROWSER_POOL_API_KEY}
MCP_POOL_SIZE=10
MCP_AUTO_SCALE=true
```

### Enterprise (On-Premise)
```env
USE_REMOTE_BROWSER=true
MCP_SERVER_TYPE=ssh
MCP_SERVER_HOST=analysis-cluster.corp
MCP_SERVER_USER=phishscope-svc
MCP_SERVER_KEY=/etc/phishscope/ssh_key
MCP_LOAD_BALANCER=true
```

## 🎯 Benefits Summary

| Feature | Local Browser | Remote Browser (MCP) |
|---------|--------------|---------------------|
| **Isolation** | ⚠️ Same machine | ✅ Complete isolation |
| **Safety** | ⚠️ Risk to host | ✅ No risk to host |
| **Scalability** | ❌ Limited | ✅ Unlimited |
| **Cost** | ✅ Free | 💰 Infrastructure cost |
| **Latency** | ✅ Fast | ⚠️ Network latency |
| **Setup** | ✅ Easy | ⚠️ Requires infrastructure |
| **Enterprise** | ❌ Not suitable | ✅ Production-ready |

## 🚦 Next Steps

Would you like me to implement:

1. **Basic MCP Server** - Core browser control server
2. **SSH Transport** - Connect to remote VM via SSH
3. **Docker Transport** - Use Docker containers
4. **Complete Solution** - All transports + documentation

Let me know which components you'd like to start with!

---

*This architecture provides enterprise-grade isolation while maintaining PhishScope's ease of use.*