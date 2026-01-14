# PhishScope Web Application & Enhanced CLI

Complete guide for using PhishScope with web interface and beautiful CLI.

## 🎯 Overview

PhishScope now includes:
1. **Web Application** - Flask-based web interface with real-time analysis
2. **Enhanced CLI** - Beautiful terminal interface with Rich library
3. **Agent-Based Architecture** - 5 specialized analysis agents

## 🏗️ Agent-Based Architecture

PhishScope uses a modular agent system:

### Analysis Agents

1. **PageLoaderAgent** - Loads URLs using Playwright with anti-detection
2. **DOMInspectorAgent** - Analyzes DOM structure for phishing indicators
3. **JavaScriptInspectorAgent** - Detects credential theft patterns in JS
4. **NetworkInspectorAgent** - Monitors traffic for data exfiltration
5. **ReportAgent** - Generates investigation-style reports

Each agent is independent and can be extended or replaced.

## 🚀 Quick Start

### Installation

```bash
cd PhishScope

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

### Option 1: Web Application (Recommended)

```bash
# Start the web server
./start_web.sh

# Or manually:
python web_app.py
```

Then open your browser to: **http://localhost:8070**

### Option 2: Enhanced CLI

```bash
# Beautiful terminal interface
python phishscope_cli.py analyze https://example.com

# With custom output directory
python phishscope_cli.py analyze https://example.com --output ./my-analysis

# Verbose mode
python phishscope_cli.py analyze https://example.com --verbose
```

### Option 3: Original CLI

```bash
# Basic CLI (still works)
python phishscope.py analyze https://example.com
```

## 🌐 Web Application Features

### User Interface
- **Modern Design** - Gradient purple theme, responsive layout
- **Real-Time Analysis** - Watch progress as analysis runs
- **Tabbed Results** - Summary, DOM, JavaScript, Network, Screenshot
- **Visual Stats** - Cards showing key metrics
- **Screenshot Display** - View captured page screenshot

### API Endpoints

```bash
# Analyze a URL
POST /api/analyze
Content-Type: application/json
{
  "url": "https://example.com"
}

# Get results
GET /api/results/<analysis_id>

# Get screenshot
GET /api/screenshot/<analysis_id>

# Get markdown report
GET /api/report/<analysis_id>

# Health check
GET /health
```

### Example API Usage

```bash
# Using curl
curl -X POST http://localhost:8070/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'

# Using Python
import requests

response = requests.post('http://localhost:8070/api/analyze', 
                        json={'url': 'https://example.com'})
result = response.json()
print(result)
```

## 💻 Enhanced CLI Features

### Visual Elements
- **Progress Bars** - Real-time progress for each analysis step
- **Colored Output** - Syntax highlighting and color-coded results
- **Tables** - Beautiful summary tables with borders
- **Panels** - Organized findings in bordered panels
- **Spinners** - Animated loading indicators

### Example Output

```
┌─────────────────────────────────────────┐
│ 🔍 PhishScope                           │
│ Evidence-Driven Phishing Analysis Agent │
└─────────────────────────────────────────┘

Target URL: https://example.com
Output Directory: ./reports/case_20260112_180000

⠋ Loading page...                    ━━━━━━━━━━━━━━━━━━━━ 100%
✓ Page loaded: Example Domain

⠋ Inspecting DOM...                  ━━━━━━━━━━━━━━━━━━━━ 100%
✓ DOM inspection complete: 0 findings

⠋ Analyzing JavaScript...            ━━━━━━━━━━━━━━━━━━━━ 100%
✓ JavaScript analysis complete: 0 patterns found

⠋ Analyzing network traffic...       ━━━━━━━━━━━━━━━━━━━━ 100%
✓ Network analysis complete: 0 exfiltration candidates

⠋ Generating report...               ━━━━━━━━━━━━━━━━━━━━ 100%
✓ Report generated: ./reports/case_20260112_180000/report.md

┌─────────────── 📊 Analysis Summary ───────────────┐
│ Metric                        │ Value             │
├───────────────────────────────┼───────────────────┤
│ Forms Detected                │ 0                 │
│ Password Fields               │ 0                 │
│ Suspicious JS Patterns        │ 0                 │
│ Exfiltration Endpoints        │ 0                 │
│ Total Network Requests        │ 1                 │
└───────────────────────────────┴───────────────────┘

┌────────────────────────────────────────────────────┐
│ ✓ Analysis Complete!                               │
│ Report saved to: ./reports/case_20260112_180000   │
└────────────────────────────────────────────────────┘
```

## 📊 Comparison: Web vs CLI

| Feature | Web App | Enhanced CLI | Original CLI |
|---------|---------|--------------|--------------|
| Real-time progress | ✅ | ✅ | ❌ |
| Visual output | ✅ | ✅ | ⚠️ Basic |
| Screenshot display | ✅ | ❌ | ❌ |
| Tabbed results | ✅ | ❌ | ❌ |
| API access | ✅ | ❌ | ❌ |
| Remote access | ✅ | ❌ | ❌ |
| Color output | ✅ | ✅ | ❌ |
| Progress bars | ✅ | ✅ | ❌ |
| Tables | ✅ | ✅ | ❌ |

## 🔧 Configuration

### Web Application

Edit `web_app.py` to change:
- Port (default: 8070)
- Host (default: 0.0.0.0)
- Debug mode (default: True)

### CLI

Both CLIs support:
- `--output` - Custom output directory
- `--verbose` - Detailed logging
- `--timeout` - Page load timeout (original CLI only)

## 📁 Output Structure

Both interfaces generate the same output:

```
reports/
└── case_20260112_180000/  (or web_20260112_180000 for web)
    ├── report.md              # Human-readable report
    ├── report.json            # Machine-readable findings
    ├── results.json           # Complete analysis data
    ├── screenshot.png         # Page screenshot
    └── artifacts/
        ├── dom_snapshot.html  # Complete DOM
        ├── network_log.json   # Network traffic
        └── inline_script_*.js # Extracted JavaScript
```

## 🔒 Security Considerations

### Web Application
- **Runs on all interfaces (0.0.0.0)** - Accessible from network
- **No authentication** - Add auth for production use
- **Loads malicious URLs** - Run in isolated environment
- **Debug mode enabled** - Disable for production

### Recommendations
1. Run in a VM or container
2. Use network isolation
3. Add authentication if exposing to network
4. Disable debug mode in production
5. Use HTTPS in production

## 🐛 Troubleshooting

### Web App Won't Start

```bash
# Check if port 8070 is in use
lsof -i :8070

# Kill process if needed
kill -9 $(lsof -t -i:8070)

# Try different port
python web_app.py  # Edit port in file
```

### CLI Shows Errors

```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Reinstall Playwright
playwright install chromium

# Check Python version
python --version  # Should be 3.9+
```

### Analysis Fails

```bash
# Enable verbose mode
python phishscope_cli.py analyze <URL> --verbose

# Check logs
tail -f phishscope.log

# Verify URL is accessible
curl -I <URL>
```

## 📚 Examples

### Web App - Analyze Phishing URL

1. Start server: `./start_web.sh`
2. Open browser: http://localhost:8070
3. Enter URL: `https://suspicious-site.com`
4. Click "Analyze URL"
5. Watch real-time progress
6. View results in tabs

### Enhanced CLI - Batch Analysis

```bash
# Analyze multiple URLs
for url in $(cat urls.txt); do
    python phishscope_cli.py analyze "$url" --output "./batch/$url"
done
```

### API - Automated Analysis

```python
import requests
import time

def analyze_url(url):
    response = requests.post('http://localhost:8070/api/analyze',
                            json={'url': url})
    data = response.json()
    
    if data['status'] == 'complete':
        print(f"Analysis complete for {url}")
        print(f"Forms: {data['results']['findings']['dom']['forms_count']}")
        print(f"JS Patterns: {len(data['results']['findings']['javascript']['suspicious_patterns'])}")
    
    return data

# Analyze URL
result = analyze_url('https://example.com')
```

## 🎓 Advanced Usage

### Custom Agent Development

```python
from agents.base_agent import BaseAgent

class CustomAgent(BaseAgent):
    async def analyze(self, page_context, output_dir):
        findings = {}
        # Your analysis logic here
        return findings
```

### Extending the Web API

```python
@app.route('/api/custom', methods=['POST'])
def custom_endpoint():
    # Your custom logic
    return jsonify({"result": "success"})
```

## 📖 Documentation

- [README.md](README.md) - Project overview
- [ARCHITECTURE.md](ARCHITECTURE.md) - Technical architecture
- [QUICKSTART.md](QUICKSTART.md) - Quick start guide
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guidelines

## 🤝 Support

- GitHub Issues: Bug reports and feature requests
- GitHub Discussions: Questions and community support

---

**Built with ❤️ for the security research community**