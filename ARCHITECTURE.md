# PhishScope Architecture

This document describes the internal architecture of PhishScope.

## Overview

PhishScope uses a modular agent-based architecture where each agent is responsible for a specific aspect of phishing analysis. The main orchestrator coordinates these agents and aggregates their findings.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         PhishScope CLI                       │
│                      (phishscope.py)                         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    Main Orchestrator                         │
│                   (PhishScope class)                         │
│  • Coordinates agent execution                               │
│  • Manages analysis pipeline                                 │
│  • Handles errors and cleanup                                │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┬──────────────┐
         ▼               ▼               ▼              ▼
┌─────────────┐  ┌─────────────┐  ┌──────────┐  ┌──────────┐
│PageLoader   │  │DOMInspector │  │JSInspect │  │Network   │
│Agent        │  │Agent        │  │or Agent  │  │Inspector │
│             │  │             │  │          │  │Agent     │
│• Load page  │  │• Find forms │  │• Extract │  │• Capture │
│• Screenshot │  │• Detect     │  │  scripts │  │  traffic │
│• Capture    │  │  inputs     │  │• Pattern │  │• Identify│
│  context    │  │• Check DOM  │  │  match   │  │  exfil   │
└─────────────┘  └─────────────┘  └──────────┘  └──────────┘
         │               │               │              │
         └───────────────┴───────────────┴──────────────┘
                         │
                         ▼
                 ┌─────────────┐
                 │ReportAgent  │
                 │             │
                 │• Aggregate  │
                 │• Generate   │
                 │  reports    │
                 └─────────────┘
```

## Core Components

### 1. CLI Entry Point (`phishscope.py`)

**Responsibilities:**
- Parse command-line arguments
- Initialize the main orchestrator
- Handle user input/output
- Display results summary

**Key Functions:**
- `main()` - Entry point
- Argument parsing with `argparse`
- Result formatting and display

### 2. Main Orchestrator (`PhishScope` class)

**Responsibilities:**
- Initialize all agents
- Execute analysis pipeline in sequence
- Pass data between agents
- Handle errors and cleanup
- Aggregate results

**Analysis Pipeline:**
```python
1. PageLoaderAgent.load_page()
   ↓ (page context, screenshot)
2. DOMInspectorAgent.inspect()
   ↓ (DOM findings)
3. JavaScriptInspectorAgent.analyze()
   ↓ (JS findings)
4. NetworkInspectorAgent.analyze()
   ↓ (network findings)
5. ReportAgent.generate_report()
   ↓ (final report)
```

### 3. PageLoaderAgent

**Purpose:** Safely load and capture phishing pages

**Key Features:**
- Headless browser automation (Playwright)
- Anti-detection measures (user-agent, viewport)
- Screenshot capture
- Network request logging
- Page context preservation

**Output:**
- Screenshot file
- Page context (for other agents)
- Network log
- Page metadata (title, final URL, status)

**Implementation Details:**
```python
- Uses Playwright's Chromium browser
- Configures realistic browser fingerprint
- Captures all network requests/responses
- Handles timeouts and errors gracefully
```

### 4. DOMInspectorAgent

**Purpose:** Analyze DOM structure for phishing indicators

**Detection Capabilities:**
- Login forms
- Password input fields
- Hidden inputs
- Suspicious iframes
- Overlay elements
- DOM mutations

**Analysis Techniques:**
- JavaScript evaluation in page context
- CSS selector queries
- Style computation
- Element visibility checks

**Output:**
- Form details (action, method, fields)
- Input field inventory
- Suspicious element list
- Evidence descriptions

### 5. JavaScriptInspectorAgent

**Purpose:** Analyze JavaScript for credential theft patterns

**Detection Patterns:**
- Event listeners (input, keydown)
- Password field access
- Fetch/XHR POST requests
- JSON serialization
- Base64 encoding
- Credential-related variables

**Analysis Techniques:**
- Script extraction (inline + external)
- Regex pattern matching
- Context extraction around matches
- Event listener detection

**Output:**
- Script inventory
- Suspicious pattern matches
- Code snippets with context
- Evidence descriptions

### 6. NetworkInspectorAgent

**Purpose:** Analyze network traffic for data exfiltration

**Detection Capabilities:**
- POST request analysis
- Suspicious endpoint identification
- Third-party domain tracking
- Exfiltration scoring

**Scoring Factors:**
- Suspicious TLDs (.tk, .ml, etc.)
- Direct IP addresses
- Non-standard ports
- Suspicious path patterns
- Data-related parameters

**Output:**
- POST request list
- Exfiltration candidates (scored)
- Third-party domain list
- Suspicious endpoint list

### 7. ReportAgent

**Purpose:** Generate investigation-style reports

**Report Types:**
- Markdown (human-readable)
- JSON (machine-readable)

**Report Sections:**
- Executive summary
- Page load information
- DOM analysis findings
- JavaScript analysis findings
- Network traffic analysis
- Conclusion with confidence level

**Confidence Levels:**
- HIGH: Multiple strong indicators
- MEDIUM: Some suspicious characteristics
- LOW: Limited indicators detected

## Data Flow

### Input
```
URL (string) → PhishScope
```

### Internal Data Flow
```
URL
  ↓
PageLoaderAgent
  ↓ page_context, network_log, screenshot
  ├→ DOMInspectorAgent → dom_findings
  ├→ JavaScriptInspectorAgent → js_findings
  └→ NetworkInspectorAgent → network_findings
       ↓
ReportAgent (aggregates all findings)
  ↓
Reports (Markdown + JSON)
```

### Output
```
reports/case_TIMESTAMP/
├── report.md
├── report.json
├── results.json
├── screenshot.png
└── artifacts/
    ├── dom_snapshot.html
    ├── network_log.json
    └── inline_script_*.js
```

## Design Principles

### 1. Modularity
- Each agent is independent
- Agents can be developed/tested separately
- Easy to add new agents

### 2. Evidence-Based
- No black-box decisions
- All findings include evidence
- Traceable analysis path

### 3. Analyst-Friendly
- Reports mimic human investigation
- Clear explanations
- Actionable findings

### 4. Security-First
- Isolated browser execution
- No credential submission
- Safe artifact handling

### 5. Extensibility
- Plugin-style agent architecture
- Clear interfaces
- TODO comments for future features

## Extension Points

### Adding a New Agent

1. Create new file in `agents/` directory
2. Implement agent class with `analyze()` method
3. Add to `agents/__init__.py`
4. Import in `phishscope.py`
5. Add to analysis pipeline
6. Update report generation

Example:
```python
class NewAgent:
    def __init__(self, logger):
        self.logger = logger
    
    async def analyze(self, input_data, output_dir):
        findings = {}
        # Analysis logic here
        return findings
```

### Adding Detection Patterns

**For JavaScript:**
- Add pattern to `SUSPICIOUS_PATTERNS` dict in `js_inspector.py`
- Add description to `_get_pattern_description()`

**For Network:**
- Add to `SUSPICIOUS_TLDS` or `LEGITIMATE_DOMAINS`
- Update scoring logic in `_identify_exfiltration()`

**For DOM:**
- Add new detection method
- Call from `inspect()` method
- Add to evidence generation

## Performance Considerations

- **Page Load:** 30s default timeout
- **Memory:** ~500MB per analysis
- **Disk:** ~5-10MB per report
- **Concurrent Analyses:** Not currently supported

## Future Architecture Improvements

1. **Async Agent Execution:** Run independent agents in parallel
2. **Caching:** Cache page loads for repeated analysis
3. **Streaming Reports:** Generate reports incrementally
4. **Plugin System:** Dynamic agent loading
5. **Distributed Analysis:** Support for analyzing multiple URLs

## Security Architecture

### Isolation Layers
1. **Browser Sandbox:** Chromium's built-in sandbox
2. **Headless Mode:** No GUI interaction
3. **Network Monitoring:** All traffic logged
4. **No Credential Submission:** Analysis only, no interaction

### Recommended Deployment
```
┌─────────────────────────────┐
│   Isolated VM/Container     │
│  ┌─────────────────────┐   │
│  │    PhishScope       │   │
│  │  ┌──────────────┐   │   │
│  │  │   Browser    │   │   │
│  │  └──────────────┘   │   │
│  └─────────────────────┘   │
│         ↓ Logs              │
│  ┌─────────────────────┐   │
│  │   Report Storage    │   │
│  └─────────────────────┘   │
└─────────────────────────────┘
         ↓ Export
    Secure Network
```

## Dependencies

- **Playwright:** Browser automation
- **Python 3.9+:** Core runtime
- **Standard Library:** All other functionality

Minimal dependencies = easier security auditing.

---

For implementation details, see the source code in each agent file.