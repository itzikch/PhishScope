"""
Unit tests for DOMInspectorAgent
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, AsyncMock
from agents.dom_inspector import DOMInspectorAgent


@pytest.mark.unit
@pytest.mark.asyncio
class TestDOMInspectorAgent:
    """Test suite for DOMInspectorAgent"""
    
    async def test_init(self, mock_logger):
        """Test DOMInspectorAgent initialization"""
        agent = DOMInspectorAgent(mock_logger)
        assert agent.logger == mock_logger
    
    async def test_inspect_no_page(self, mock_logger, temp_output_dir):
        """Test inspection with no page context"""
        agent = DOMInspectorAgent(mock_logger)
        
        # Execute with None page
        findings = await agent.inspect(None, temp_output_dir)
        
        # Verify default structure
        assert findings["forms_count"] == 0
        assert findings["password_fields"] == []
        assert findings["hidden_inputs"] == []
        assert findings["suspicious_iframes"] == []
        assert findings["overlays"] == []
        
        # Verify warning was logged
        mock_logger.warning.assert_called_once()
    
    async def test_inspect_with_forms(self, mock_logger, temp_output_dir, mock_page_context):
        """Test detection of forms"""
        agent = DOMInspectorAgent(mock_logger)
        
        # Mock form detection
        mock_page_context.evaluate = AsyncMock(side_effect=[
            # Forms
            [
                {
                    "index": 0,
                    "action": "https://evil.com/steal",
                    "method": "POST",
                    "id": "loginForm",
                    "class": "login",
                    "input_count": 2,
                    "has_password": True,
                    "has_email": True,
                    "has_submit": True
                }
            ],
            # Password fields
            [{"index": 0, "id": "pwd", "name": "password", "placeholder": "Password", "autocomplete": "off", "required": True, "visible": True}],
            # Hidden inputs
            [],
            # Iframes
            [],
            # Overlays
            []
        ])
        mock_page_context.content = AsyncMock(return_value="<html><body>Test</body></html>")
        
        # Execute
        findings = await agent.inspect(mock_page_context, temp_output_dir)
        
        # Verify
        assert findings["forms_count"] == 1
        assert len(findings["forms"]) == 1
        assert findings["forms"][0]["action"] == "https://evil.com/steal"
        assert findings["forms"][0]["has_password"] is True
        assert len(findings["password_fields"]) == 1
        assert len(findings["evidence"]) > 0
    
    async def test_inspect_with_password_fields(self, mock_logger, temp_output_dir, mock_page_context):
        """Test detection of password fields"""
        agent = DOMInspectorAgent(mock_logger)
        
        # Mock password field detection
        mock_page_context.evaluate = AsyncMock(side_effect=[
            [],  # Forms
            [
                {
                    "index": 0,
                    "id": "password",
                    "name": "pwd",
                    "placeholder": "Enter password",
                    "autocomplete": "current-password",
                    "required": True,
                    "visible": True
                },
                {
                    "index": 1,
                    "id": "confirm_password",
                    "name": "pwd2",
                    "placeholder": "Confirm password",
                    "autocomplete": "new-password",
                    "required": True,
                    "visible": True
                }
            ],
            [],  # Hidden inputs
            [],  # Iframes
            []   # Overlays
        ])
        mock_page_context.content = AsyncMock(return_value="<html><body>Test</body></html>")
        
        # Execute
        findings = await agent.inspect(mock_page_context, temp_output_dir)
        
        # Verify
        assert len(findings["password_fields"]) == 2
        assert findings["password_fields"][0]["name"] == "pwd"
        assert findings["password_fields"][1]["name"] == "pwd2"
        assert any("password input field" in e for e in findings["evidence"])
    
    async def test_inspect_with_hidden_inputs(self, mock_logger, temp_output_dir, mock_page_context):
        """Test detection of hidden inputs"""
        agent = DOMInspectorAgent(mock_logger)
        
        # Mock hidden input detection
        mock_page_context.evaluate = AsyncMock(side_effect=[
            [],  # Forms
            [],  # Password fields
            [
                {"index": 0, "name": "csrf_token", "value": "abc123", "id": "csrf"},
                {"index": 1, "name": "tracking_id", "value": "xyz789", "id": None}
            ],
            [],  # Iframes
            []   # Overlays
        ])
        mock_page_context.content = AsyncMock(return_value="<html><body>Test</body></html>")
        
        # Execute
        findings = await agent.inspect(mock_page_context, temp_output_dir)
        
        # Verify
        assert len(findings["hidden_inputs"]) == 2
        assert findings["hidden_inputs"][0]["name"] == "csrf_token"
        assert any("hidden input field" in e for e in findings["evidence"])
    
    async def test_inspect_with_iframes(self, mock_logger, temp_output_dir, mock_page_context):
        """Test detection of iframes"""
        agent = DOMInspectorAgent(mock_logger)
        
        # Mock iframe detection
        mock_page_context.evaluate = AsyncMock(side_effect=[
            [],  # Forms
            [],  # Password fields
            [],  # Hidden inputs
            [
                {
                    "index": 0,
                    "src": "https://evil.com/fake-login",
                    "width": "100%",
                    "height": "500",
                    "sandbox": None,
                    "hidden": False
                }
            ],
            []   # Overlays
        ])
        mock_page_context.content = AsyncMock(return_value="<html><body>Test</body></html>")
        
        # Execute
        findings = await agent.inspect(mock_page_context, temp_output_dir)
        
        # Verify
        assert len(findings["suspicious_iframes"]) == 1
        assert findings["suspicious_iframes"][0]["src"] == "https://evil.com/fake-login"
        assert any("iframe" in e.lower() for e in findings["evidence"])
    
    async def test_inspect_with_overlays(self, mock_logger, temp_output_dir, mock_page_context):
        """Test detection of overlays"""
        agent = DOMInspectorAgent(mock_logger)
        
        # Mock overlay detection
        mock_page_context.evaluate = AsyncMock(side_effect=[
            [],  # Forms
            [],  # Password fields
            [],  # Hidden inputs
            [],  # Iframes
            [
                {
                    "index": 0,
                    "id": "modal",
                    "class": "overlay-modal",
                    "position": "fixed",
                    "zIndex": "9999",
                    "has_form": True
                }
            ]
        ])
        mock_page_context.content = AsyncMock(return_value="<html><body>Test</body></html>")
        
        # Execute
        findings = await agent.inspect(mock_page_context, temp_output_dir)
        
        # Verify
        assert len(findings["overlays"]) == 1
        assert findings["overlays"][0]["has_form"] is True
        assert any("overlay" in e.lower() for e in findings["evidence"])
    
    async def test_inspect_saves_dom_snapshot(self, mock_logger, temp_output_dir, mock_page_context):
        """Test that DOM snapshot is saved"""
        agent = DOMInspectorAgent(mock_logger)
        
        # Mock all evaluations
        mock_page_context.evaluate = AsyncMock(return_value=[])
        mock_page_context.content = AsyncMock(return_value="<html><body><h1>Test Page</h1></body></html>")
        
        # Execute
        findings = await agent.inspect(mock_page_context, temp_output_dir)
        
        # Verify DOM snapshot was saved
        dom_snapshot_path = temp_output_dir / "artifacts" / "dom_snapshot.html"
        assert dom_snapshot_path.exists()
        
        # Verify content
        content = dom_snapshot_path.read_text()
        assert "<h1>Test Page</h1>" in content
    
    async def test_inspect_handles_errors(self, mock_logger, temp_output_dir, mock_page_context):
        """Test error handling during inspection"""
        agent = DOMInspectorAgent(mock_logger)
        
        # Mock evaluation to raise error
        mock_page_context.evaluate = AsyncMock(side_effect=Exception("Evaluation failed"))
        
        # Execute
        findings = await agent.inspect(mock_page_context, temp_output_dir)
        
        # Verify error was captured
        assert "error" in findings
        assert "Evaluation failed" in findings["error"]
        mock_logger.error.assert_called()
    
    async def test_generate_evidence_comprehensive(self, mock_logger):
        """Test evidence generation with multiple findings"""
        agent = DOMInspectorAgent(mock_logger)
        
        # Create comprehensive findings
        findings = {
            "forms_count": 2,
            "forms": [
                {
                    "has_password": True,
                    "action": "https://evil.com/steal"
                },
                {
                    "has_password": False,
                    "action": "none"
                }
            ],
            "password_fields": [{"id": "pwd1"}, {"id": "pwd2"}],
            "hidden_inputs": [{"name": "token"}],
            "suspicious_iframes": [{"src": "evil.com"}],
            "overlays": [{"id": "modal"}]
        }
        
        # Generate evidence
        evidence = agent._generate_evidence(findings)
        
        # Verify comprehensive evidence
        assert len(evidence) >= 5
        assert any("2 form(s)" in e for e in evidence)
        assert any("password input field" in e for e in evidence)
        assert any("hidden input field" in e for e in evidence)
        assert any("iframe" in e for e in evidence)
        assert any("overlay" in e for e in evidence)
    
    async def test_detect_forms_with_no_action(self, mock_logger, temp_output_dir, mock_page_context):
        """Test detection of forms with no action (JavaScript-based)"""
        agent = DOMInspectorAgent(mock_logger)
        
        # Mock form with no action
        mock_page_context.evaluate = AsyncMock(side_effect=[
            [
                {
                    "index": 0,
                    "action": "none",
                    "method": "POST",
                    "id": "jsForm",
                    "class": "",
                    "input_count": 2,
                    "has_password": True,
                    "has_email": False,
                    "has_submit": True
                }
            ],
            [],  # Password fields
            [],  # Hidden inputs
            [],  # Iframes
            []   # Overlays
        ])
        mock_page_context.content = AsyncMock(return_value="<html><body>Test</body></html>")
        
        # Execute
        findings = await agent.inspect(mock_page_context, temp_output_dir)
        
        # Verify evidence mentions JavaScript-based submission
        assert any("JavaScript-based submission" in e for e in findings["evidence"])


@pytest.mark.integration
@pytest.mark.requires_browser
@pytest.mark.asyncio
class TestDOMInspectorIntegration:
    """Integration tests for DOMInspectorAgent"""
    
    async def test_inspect_real_phishing_page(self, mock_logger, temp_output_dir, browser_context, sample_phishing_html):
        """Test inspection of a real phishing page"""
        agent = DOMInspectorAgent(mock_logger)
        
        # Create a page with phishing HTML
        page = await browser_context.new_page()
        await page.set_content(sample_phishing_html)
        
        # Execute
        findings = await agent.inspect(page, temp_output_dir)
        
        # Verify
        assert findings["forms_count"] > 0
        assert len(findings["password_fields"]) > 0
        assert len(findings["evidence"]) > 0
        
        # Cleanup
        await page.close()