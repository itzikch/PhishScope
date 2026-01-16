# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Project: PhishScope - Evidence-Driven Phishing Analysis Agent

Python 3.9+ phishing analysis tool using Playwright for browser automation, Flask for web interface, and optional multi-provider LLM integration (IBM WatsonX or RITS).

## Commands

```bash
# Setup
pip install -r requirements.txt
playwright install chromium

# Run CLI analysis
python phishscope.py analyze <url>
python phishscope_cli.py analyze <url>  # Enhanced CLI with Rich formatting

# Run web interface
python web_app.py  # Starts on http://localhost:8070
./start_web.sh     # Alternative startup script

# No test suite exists - project has no pytest/unittest tests
```

## Critical Non-Obvious Patterns

### 1. Page Context Serialization Issue ⚠️
**CRITICAL**: `page_loader.load_page()` returns a dict containing a `page_context` key with a Playwright Page object. This MUST be extracted using `.pop("page_context", None)` before storing results in any dict that will be JSON serialized. Failure to do this causes serialization errors.

```python
# CORRECT pattern (see phishscope.py:79, web_app.py:67)
page_data = await self.page_loader.load_page(self.url, self.output_dir)
page_context = page_data.pop("page_context", None)  # Extract before storing
results["page_load"] = page_data  # Now safe to serialize
```

### 2. Network Logging via Closures
Network traffic is captured using nested async functions (closures) inside `page_loader.load_page()`:

```python
# Pattern in agents/page_loader.py:75-90
network_log = []

async def log_request(request):
    network_log.append({...})

async def log_response(response):
    network_log.append({...})

page.on("request", log_request)
page.on("response", log_response)
```

This non-standard pattern means network_log is a closure variable, not a class attribute. When modifying page loading, preserve this pattern.

### 3. Multi-Provider LLM Architecture
LLM provider is selected via `LLM_PROVIDER` environment variable (watsonx or rits):

- **WatsonX**: Requires IAM token refresh via IBM Cloud API (`_get_iam_token()`)
- **RITS**: OpenAI-compatible API with different endpoint structure
- Always check `llm_agent.is_available()` before using AI features
- Each provider has different initialization in `agents/llm_agent.py`

### 4. Agent Lifecycle Pattern
All agents (PageLoaderAgent, DOMInspectorAgent, etc.) are:
- **Stateless** - new instances created per analysis
- Require logger instance in `__init__`
- No shared state between agents except through results dict
- `page_loader.cleanup()` MUST be called in finally block to close browser

### 5. Output Directory Conventions
Hardcoded directory structure (not configurable):
- CLI: `./reports/case_TIMESTAMP/`
- Web: `./reports/web_TIMESTAMP/`
- Artifacts: `output_dir/artifacts/` for JS snippets and DOM snapshots

### 6. Optional Dependency Pattern
`python-dotenv` is optional - code uses try/except import pattern:

```python
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # Falls back to system environment variables
```

This pattern is repeated in phishscope.py, web_app.py, and phishscope_cli.py.

## Code Style

- **Async/await**: All agent methods are async (except LLMAgent which uses sync HTTP)
- **Type hints**: Used for function signatures (Dict, Any, List, Optional, Path)
- **Logging**: All agents use injected logger, not module-level logging
- **Error handling**: Try/except with logger.error() and exc_info=True for tracebacks
- **Docstrings**: Google-style docstrings for classes and public methods

## Environment Variables

See `.env.example` for full list. Critical non-obvious ones:

- `LLM_PROVIDER`: Must be exactly "watsonx" or "rits" (lowercase)
- `WATSONX_API_KEY`: Required for WatsonX, triggers IAM token flow
- `RITS_API_KEY`: Required for RITS provider
- Web app uses port 8070 (hardcoded in web_app.py, not configurable via env)

## Security Notes

- Always run in isolated environment (VM/container)
- Loads potentially malicious URLs with Playwright
- No input sanitization on URLs (by design - analysis tool)
- Network logs may contain sensitive data