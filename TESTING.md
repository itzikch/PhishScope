# PhishScope Testing Guide

This document describes the testing infrastructure and best practices for PhishScope.

## Table of Contents

- [Overview](#overview)
- [Test Structure](#test-structure)
- [Running Tests](#running-tests)
- [Test Categories](#test-categories)
- [Writing Tests](#writing-tests)
- [CI/CD Pipeline](#cicd-pipeline)
- [Coverage Reports](#coverage-reports)

## Overview

PhishScope uses **pytest** as its testing framework with comprehensive test coverage across:
- Unit tests for individual agents
- Integration tests for the full analysis pipeline
- Browser-based tests using Playwright
- Mock-based tests for faster execution

## Test Structure

```
tests/
├── conftest.py                 # Shared fixtures and configuration
├── test_page_loader.py         # PageLoaderAgent tests
├── test_dom_inspector.py       # DOMInspectorAgent tests
├── test_js_inspector.py        # JavaScriptInspectorAgent tests
├── test_network_inspector.py   # NetworkInspectorAgent tests
├── test_report_agent.py        # ReportAgent tests
├── test_llm_agent.py           # LLMAgent tests
└── test_integration.py         # Full pipeline integration tests
```

## Running Tests

### Install Test Dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

### Run All Tests

```bash
pytest
```

### Run Specific Test Categories

```bash
# Unit tests only (fast)
pytest -m unit

# Integration tests (without browser)
pytest -m "integration and not requires_browser"

# Browser-based tests (slow)
pytest -m requires_browser

# Tests requiring AI credentials
pytest -m requires_ai
```

### Run Tests with Coverage

```bash
# Generate coverage report
pytest --cov=agents --cov=utils --cov-report=html --cov-report=term-missing

# View HTML coverage report
open htmlcov/index.html
```

### Run Specific Test Files

```bash
# Test a specific agent
pytest tests/test_page_loader.py -v

# Test a specific function
pytest tests/test_page_loader.py::TestPageLoaderAgent::test_load_page_success -v
```

### Run Tests in Parallel

```bash
# Install pytest-xdist
pip install pytest-xdist

# Run tests in parallel
pytest -n auto
```

## Test Categories

Tests are organized using pytest markers:

### `@pytest.mark.unit`
Fast unit tests that mock external dependencies. Run these frequently during development.

```python
@pytest.mark.unit
@pytest.mark.asyncio
async def test_init(self, mock_logger):
    agent = PageLoaderAgent(mock_logger)
    assert agent.logger == mock_logger
```

### `@pytest.mark.integration`
Integration tests that test multiple components together. May use mocks for expensive operations.

```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_full_analysis_pipeline_mock(self, mock_logger, temp_output_dir):
    # Test complete pipeline with mocked browser
    pass
```

### `@pytest.mark.requires_browser`
Tests that require a real Playwright browser. These are slower but more comprehensive.

```python
@pytest.mark.integration
@pytest.mark.requires_browser
@pytest.mark.slow
@pytest.mark.asyncio
async def test_load_real_page(self, mock_logger, temp_output_dir):
    # Test with real browser
    pass
```

### `@pytest.mark.requires_ai`
Tests that require AI provider credentials (WatsonX or RITS). Skipped if credentials not available.

```python
@pytest.mark.integration
@pytest.mark.requires_ai
def test_real_watsonx_analysis(self, mock_logger):
    if not os.getenv('WATSONX_API_KEY'):
        pytest.skip("WatsonX credentials not available")
    # Test with real AI
    pass
```

### `@pytest.mark.slow`
Tests that take significant time to run. Useful for excluding from quick test runs.

```bash
# Skip slow tests
pytest -m "not slow"
```

## Writing Tests

### Test Fixtures

Common fixtures are defined in `tests/conftest.py`:

```python
# Mock logger
def test_something(mock_logger):
    agent = MyAgent(mock_logger)
    # ...

# Temporary output directory
def test_something(temp_output_dir):
    # temp_output_dir is automatically cleaned up
    pass

# Sample phishing HTML
def test_something(sample_phishing_html):
    # Use pre-defined phishing page HTML
    pass

# Mock page context
def test_something(mock_page_context):
    # Mock Playwright Page object
    pass

# Sample findings
def test_something(sample_dom_findings, sample_js_findings, sample_network_findings):
    # Use pre-defined analysis findings
    pass
```

### Async Tests

Use `@pytest.mark.asyncio` for async test functions:

```python
@pytest.mark.asyncio
async def test_async_function(self):
    result = await some_async_function()
    assert result is not None
```

### Mocking

Use `unittest.mock` for mocking:

```python
from unittest.mock import Mock, AsyncMock, patch

# Mock synchronous function
mock_func = Mock(return_value="test")

# Mock async function
mock_async = AsyncMock(return_value="test")

# Patch during test
with patch('module.function') as mock_func:
    mock_func.return_value = "test"
    # test code
```

### Test Naming Conventions

- Test files: `test_<module_name>.py`
- Test classes: `Test<ClassName>`
- Test functions: `test_<what_is_being_tested>`

```python
class TestPageLoaderAgent:
    async def test_load_page_success(self):
        # Test successful page loading
        pass
    
    async def test_load_page_timeout(self):
        # Test timeout handling
        pass
```

## CI/CD Pipeline

PhishScope uses GitHub Actions for continuous integration:

### Workflows

1. **Unit Tests** - Run on every push/PR
   - Tests across Python 3.9, 3.10, 3.11, 3.12
   - Fast unit tests with mocked dependencies
   - Coverage reporting to Codecov

2. **Integration Tests** - Run on every push/PR
   - Integration tests without browser
   - Tests component interactions

3. **Browser Tests** - Run on every push/PR
   - Full integration tests with Playwright
   - Tests real browser interactions
   - Timeout: 10 minutes

4. **Linting** - Run on every push/PR
   - flake8 for code quality
   - black for code formatting
   - isort for import sorting

5. **Security Scanning** - Run on every push/PR
   - bandit for security issues
   - safety for dependency vulnerabilities

### Running CI Locally

Simulate CI environment locally:

```bash
# Run all unit tests
pytest -m unit --cov=agents --cov=utils --cov-report=term-missing

# Run integration tests
pytest -m "integration and not requires_browser"

# Run linting
flake8 agents/ utils/
black --check agents/ utils/
isort --check-only agents/ utils/

# Run security scans
bandit -r agents/ utils/
safety check
```

## Coverage Reports

### Generate Coverage Report

```bash
# Terminal report
pytest --cov=agents --cov=utils --cov-report=term-missing

# HTML report
pytest --cov=agents --cov=utils --cov-report=html
open htmlcov/index.html

# XML report (for CI)
pytest --cov=agents --cov=utils --cov-report=xml
```

### Coverage Goals

- **Overall Coverage**: Target 80%+
- **Critical Paths**: Target 90%+
  - Page loading and browser interaction
  - Data exfiltration detection
  - Report generation

### Viewing Coverage in CI

Coverage reports are automatically uploaded to Codecov on every CI run. View them at:
```
https://codecov.io/gh/yourusername/PhishScope
```

## Best Practices

### 1. Test Isolation
Each test should be independent and not rely on other tests:

```python
# Good - uses fixture for clean state
async def test_something(temp_output_dir):
    agent = MyAgent()
    result = await agent.process(temp_output_dir)
    assert result is not None

# Bad - relies on global state
global_agent = None
async def test_something():
    global global_agent
    if not global_agent:
        global_agent = MyAgent()
    # ...
```

### 2. Mock External Dependencies
Mock expensive or unreliable external dependencies:

```python
# Good - mocks browser
with patch.object(agent.page_loader, 'load_page') as mock_load:
    mock_load.return_value = {"success": True}
    result = await agent.analyze()

# Bad - uses real browser in unit test
result = await agent.analyze()  # Slow and brittle
```

### 3. Test Edge Cases
Test both success and failure scenarios:

```python
async def test_load_page_success(self):
    # Test normal operation
    pass

async def test_load_page_timeout(self):
    # Test timeout handling
    pass

async def test_load_page_invalid_url(self):
    # Test error handling
    pass
```

### 4. Use Descriptive Assertions
Make test failures easy to understand:

```python
# Good
assert len(findings["forms"]) == 2, "Expected 2 forms but found different count"

# Bad
assert len(findings["forms"]) == 2
```

### 5. Keep Tests Fast
- Use mocks for unit tests
- Reserve real browser tests for integration tests
- Mark slow tests with `@pytest.mark.slow`

## Troubleshooting

### Tests Fail Locally But Pass in CI

- Check Python version (CI uses 3.9-3.12)
- Ensure all dependencies are installed
- Check for environment-specific issues

### Browser Tests Timeout

- Increase timeout in test: `@pytest.mark.timeout(60)`
- Check network connectivity
- Verify Playwright browsers are installed

### Coverage Not Generated

- Ensure pytest-cov is installed: `pip install pytest-cov`
- Check that source paths are correct in pytest.ini
- Verify tests are actually running

### Import Errors

- Ensure PhishScope is in PYTHONPATH
- Install in development mode: `pip install -e .`
- Check for circular imports

## Contributing

When adding new features:

1. Write tests first (TDD approach)
2. Ensure all tests pass: `pytest`
3. Check coverage: `pytest --cov`
4. Run linting: `flake8 agents/ utils/`
5. Update this documentation if needed

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [Playwright Python](https://playwright.dev/python/)
- [unittest.mock](https://docs.python.org/3/library/unittest.mock.html)

---

**Questions?** Open an issue or contact the maintainers.