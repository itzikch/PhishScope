# PhishScope 🔍

**Evidence-Driven Phishing Analysis Agent**

PhishScope is an open-source tool designed for SOC analysts and threat researchers to analyze phishing webpages the way a human investigator would. Instead of providing binary classifications, PhishScope produces detailed investigation reports with concrete forensic evidence.

## 🎯 What PhishScope Does

PhishScope automatically:
- Loads suspicious URLs in a controlled environment
- Captures screenshots and DOM snapshots
- Analyzes JavaScript behavior for credential theft patterns
- Monitors network traffic for data exfiltration
- Generates human-readable investigation reports
- **Runs adversarial AI debates** to reach a verdict from multiple perspectives

## 🚫 What PhishScope Does NOT Do

- ML-based URL classification
- Reputation scoring
- Email analysis
- Real-time blocking

## 🏗️ Architecture

PhishScope uses a modular agent-based architecture with optional AI enhancement:

### Core Agents

1. **PageLoaderAgent** - Safe page loading with anti-detection
2. **DOMInspectorAgent** - Form detection and DOM mutation analysis
3. **JavaScriptInspectorAgent** - Credential theft pattern detection
4. **NetworkInspectorAgent** - Traffic analysis and exfiltration detection
5. **LLMAgent** - 🤖 AI-powered intelligent analysis (optional, multi-provider)
6. **ReportAgent** - Evidence aggregation and report generation

### AI Enhancement (Optional)

PhishScope supports **multiple LLM providers** for intelligent phishing analysis:

**Supported Providers:**
- **IBM WatsonX** - Enterprise-grade AI with Granite models
- **RITS** - OpenAI-compatible API with custom models
- **OpenAI** - GPT models via OpenAI API
- **Ollama** - Local models (no API key required)

**AI Capabilities:**
- AI-powered phishing assessment with confidence scoring
- Natural language reasoning and explanations
- Attack methodology analysis
- Threat intelligence generation
- Security recommendations
- **Multi-agent adversarial debate** for deeper analysis

**Easy Provider Switching:** Simply change `LLM_PROVIDER` in `.env` - no code changes needed!

## 🥊 Multi-Agent Debate Mode

PhishScope features an **adversarial debate system** where three specialized AI agents analyze a URL through structured argumentation — providing a more thorough and transparent verdict than a single AI call.

### How It Works

```
1. Page Scraping    → Collect forensic evidence
2. Prosecutor 🔴   → Opening arguments (phishing indicators)
3. Defense 🟢      → Opening arguments (legitimacy indicators)
4. Prosecutor 🔴   → Rebuttal to defense
5. Defense 🟢      → Rebuttal to prosecution
6. Judge ⚖️        → Final ruling with risk score (0–100)
```

### The Three Agents

| Agent | Role | Focus |
|-------|------|-------|
| 🔴 **Prosecutor** | Argues the site IS phishing | Typosquatting, SSL issues, urgency language, suspicious forms |
| 🟢 **Defense Attorney** | Argues the site IS legitimate | Valid SSL, professional design, logical purpose |
| ⚖️ **Judge** | Issues final verdict | Weighs both sides, outputs risk score + verdict |

### Verdict Types

- **PHISHING** 🚨 - Strong evidence of malicious intent
- **SUSPICIOUS** ⚠️ - Inconclusive, warrants further investigation
- **LEGITIMATE** ✅ - No significant phishing indicators found

### Real-Time Streaming

The debate streams live via **Server-Sent Events (SSE)** — watch the analysis unfold argument by argument in the web UI.

### API Usage

```bash
POST /api/analyze/debate
Content-Type: application/json

{"url": "https://suspicious-site.example.com"}
```

Response is an SSE stream with events: `scrape_done`, `agent`, `verdict`, `done`.

See [DEBATE_MODE.md](DEBATE_MODE.md) for full documentation.

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/itzikch/PhishScope.git
cd PhishScope

# Install dependencies
pip install -e .

# Install Playwright browsers
playwright install chromium
```

### Basic Usage

```bash
# Analyze a suspicious URL (with AI if configured)
phishscope analyze https://suspicious-site.example.com

# Specify output directory
phishscope analyze https://suspicious-site.example.com --output ./reports/case001

# Enable verbose logging
phishscope analyze https://suspicious-site.example.com --verbose

# Disable AI (use rule-based analysis only)
phishscope analyze https://suspicious-site.example.com --no-ai
```

### Web Interface (React + Vite)

PhishScope includes a modern React web UI with real-time analysis and debate mode!

```bash
# Quick start - automated setup and launch
./start_web_ui.sh

# Or manual setup:
# 1. Install package in editable mode
pip install -e .

# 2. Start backend API (Terminal 1)
uvicorn src.phishscope.api.main:app --host 0.0.0.0 --port 8070 --reload

# 3. Start frontend dev server (Terminal 2)
cd frontend
npm install  # First time only
npm run dev

# Visit http://localhost:3000 (frontend)
# API docs at http://localhost:8070/docs
```

**Web UI Features:**
- 🎯 Real-time URL analysis with progress tracking
- 🥊 **Multi-agent debate mode** with live streaming
- 📊 Interactive results dashboard
- 🖼️ Screenshot viewer
- 📝 Detailed findings panels (DOM, JS, Network)
- 🤖 AI analysis results (when configured)
- 📄 Markdown report viewer
- 📱 Responsive design with TailwindCSS
- 🌙 Dark/light theme toggle

See [START_WEB_UI.md](START_WEB_UI.md) for detailed setup instructions.

## 📊 Output Format

PhishScope generates:
- **JSON report** - Machine-readable findings
- **Markdown report** - Human-readable investigation summary
- **Screenshot** - Visual evidence
- **Network logs** - Captured traffic
- **JavaScript artifacts** - Suspicious code snippets

### Example Report Structure

```
reports/
└── case_20260112_174300/
    ├── report.json          # Structured findings
    ├── report.md            # Investigation summary
    ├── screenshot.png       # Page screenshot
    ├── network_log.json     # Network traffic
    └── artifacts/
        ├── suspicious_js_1.js
        └── dom_snapshot.html
```

## 🔬 Use Cases

- **SOC Analysis** - Investigate reported phishing URLs
- **Threat Research** - Study phishing techniques and TTPs
- **Training** - Demonstrate phishing mechanics

## 🛠️ Technical Stack

- **Language**: Python 3.9+
- **Browser Automation**: Playwright
- **Output**: JSON + Markdown
- **Dependencies**: Minimal, no cloud services required

## 📋 Requirements

- Python 3.9 or higher
- 2GB RAM minimum
- Internet connection (for analyzing live URLs)
- Chromium browser (installed via Playwright)

## 🔒 Security Considerations

PhishScope loads potentially malicious content. Always run in:
- Isolated VM or container
- Network with proper egress filtering
- Non-production environment

**Never analyze phishing URLs on your primary workstation.**

## 🐛 Bug Reports & Feature Requests

Please use GitHub Issues for:
- Bug reports
- Feature requests
- Documentation improvements

## 📞 Contact

- GitHub: [@itzikch](https://github.com/itzikch)


**⚠️ Disclaimer**: PhishScope is for authorized security research and analysis only. Users are responsible for compliance with applicable laws and regulations.