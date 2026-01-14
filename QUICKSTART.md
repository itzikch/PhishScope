# PhishScope Quick Start Guide

Get up and running with PhishScope in 5 minutes.

## Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- 2GB RAM minimum
- Internet connection

## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/PhishScope.git
cd PhishScope
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

### Step 4: Verify Installation

```bash
# Check if PhishScope is working
python phishscope.py --version
```

## Basic Usage

### Analyze a URL

```bash
python phishscope.py analyze https://example-phishing-site.com
```

This will:
1. Load the page safely in a headless browser
2. Capture a screenshot
3. Analyze DOM, JavaScript, and network traffic
4. Generate a report in `./reports/case_TIMESTAMP/`

### View the Report

```bash
# Navigate to the report directory
cd reports/case_20260112_173000/

# View the Markdown report
cat report.md

# Or open in your browser
open report.md  # macOS
xdg-open report.md  # Linux
start report.md  # Windows
```

## Advanced Usage

### Specify Output Directory

```bash
python phishscope.py analyze https://phishing-site.com --output ./my-analysis
```

### Enable Verbose Logging

```bash
python phishscope.py analyze https://phishing-site.com --verbose
```

### Custom Timeout

```bash
python phishscope.py analyze https://phishing-site.com --timeout 60
```

## Understanding the Output

PhishScope generates several files:

```
reports/case_20260112_173000/
├── report.md                    # Human-readable investigation report
├── report.json                  # Machine-readable findings
├── results.json                 # Complete analysis results
├── screenshot.png               # Page screenshot
└── artifacts/
    ├── dom_snapshot.html        # Complete DOM
    ├── network_log.json         # Network traffic
    ├── inline_script_0.js       # Extracted JavaScript
    ├── inline_script_1.js
    └── suspicious_js_snippets.txt
```

### Key Sections in report.md

1. **Executive Summary** - High-level overview
2. **Page Load Information** - URL, title, status
3. **DOM Analysis** - Forms, inputs, overlays
4. **JavaScript Analysis** - Suspicious patterns
5. **Network Traffic Analysis** - Exfiltration endpoints
6. **Conclusion** - Confidence assessment

## Example Workflow

### 1. Receive Phishing Report

You receive a suspicious URL from a user: `https://secure-verify-account.tk/login`

### 2. Analyze with PhishScope

```bash
python phishscope.py analyze https://secure-verify-account.tk/login \
  --output ./cases/user_report_001 \
  --verbose
```

### 3. Review Findings

```bash
cd cases/user_report_001
cat report.md
```

### 4. Share with Team

```bash
# The report is self-contained and can be shared
zip -r user_report_001.zip user_report_001/
```

## Safety Tips

⚠️ **IMPORTANT SECURITY WARNINGS**

1. **Always run in an isolated environment**
   - Use a VM or container
   - Never run on your primary workstation

2. **Network isolation**
   - Consider using a separate network
   - Monitor outbound connections

3. **Don't interact with the page**
   - PhishScope loads pages automatically
   - Don't manually browse to phishing URLs

4. **Handle credentials carefully**
   - Never enter real credentials
   - Reports may contain sensitive data

## Troubleshooting

### "playwright not found"

```bash
pip install playwright
playwright install chromium
```

### "Permission denied"

```bash
chmod +x phishscope.py
```

### "Module not found"

Make sure you're in the PhishScope directory and virtual environment is activated:

```bash
cd PhishScope
source venv/bin/activate  # or venv\Scripts\activate on Windows
```

### Page won't load

- Check your internet connection
- Try increasing timeout: `--timeout 60`
- Some sites may block headless browsers
- Enable verbose mode to see detailed errors: `--verbose`

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check [EXAMPLE_REPORT.md](EXAMPLE_REPORT.md) to see sample output
- Review [CONTRIBUTING.md](CONTRIBUTING.md) to contribute
- Explore the `agents/` directory to understand the architecture

## Getting Help

- GitHub Issues: Report bugs or request features
- GitHub Discussions: Ask questions
- Documentation: Read the code comments

## Quick Reference

```bash
# Basic analysis
python phishscope.py analyze <URL>

# With options
python phishscope.py analyze <URL> --output <DIR> --verbose --timeout <SECONDS>

# Help
python phishscope.py --help
python phishscope.py analyze --help
```

---

Happy phishing analysis! 🔍