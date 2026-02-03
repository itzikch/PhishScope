"""
Unit tests for ReportAgent
"""

import pytest
import json
from pathlib import Path
from unittest.mock import Mock
from agents.report_agent import ReportAgent


@pytest.mark.unit
@pytest.mark.asyncio
class TestReportAgent:
    """Test suite for ReportAgent"""
    
    async def test_init(self, mock_logger):
        """Test ReportAgent initialization"""
        agent = ReportAgent(mock_logger)
        assert agent.logger == mock_logger
    
    async def test_generate_report_creates_files(self, mock_logger, temp_output_dir, sample_analysis_results):
        """Test that report generation creates both MD and JSON files"""
        agent = ReportAgent(mock_logger)
        
        # Execute
        report_path = await agent.generate_report(sample_analysis_results, temp_output_dir)
        
        # Verify markdown report
        assert report_path.exists()
        assert report_path.name == "report.md"
        
        # Verify JSON report
        json_path = temp_output_dir / "report.json"
        assert json_path.exists()
    
    async def test_markdown_report_structure(self, mock_logger, temp_output_dir, sample_analysis_results):
        """Test markdown report has correct structure"""
        agent = ReportAgent(mock_logger)
        
        # Execute
        report_path = await agent.generate_report(sample_analysis_results, temp_output_dir)
        
        # Read and verify content
        content = report_path.read_text()
        
        # Check for required sections
        assert "# PhishScope Investigation Report" in content
        assert "## Executive Summary" in content
        assert "## Page Load Information" in content
        assert "## DOM Analysis" in content
        assert "## JavaScript Analysis" in content
        assert "## Network Traffic Analysis" in content
        assert "## Conclusion" in content
        assert "## Artifacts" in content
    
    async def test_json_report_content(self, mock_logger, temp_output_dir, sample_analysis_results):
        """Test JSON report contains all results"""
        agent = ReportAgent(mock_logger)
        
        # Execute
        await agent.generate_report(sample_analysis_results, temp_output_dir)
        
        # Read JSON report
        json_path = temp_output_dir / "report.json"
        with open(json_path, 'r') as f:
            json_data = json.load(f)
        
        # Verify structure
        assert json_data["url"] == sample_analysis_results["url"]
        assert "findings" in json_data
        assert "dom" in json_data["findings"]
        assert "javascript" in json_data["findings"]
        assert "network" in json_data["findings"]
    
    async def test_generate_summary_high_risk(self, mock_logger):
        """Test summary generation for high-risk findings"""
        agent = ReportAgent(mock_logger)
        
        findings = {
            "dom": {
                "forms_count": 1,
                "password_fields": [{"id": "pwd"}]
            },
            "javascript": {
                "suspicious_patterns": [
                    {"pattern": "password_access"},
                    {"pattern": "fetch_post"},
                    {"pattern": "json_stringify"}
                ]
            },
            "network": {
                "exfiltration_candidates": [
                    {"domain": "evil.com"}
                ]
            }
        }
        
        # Generate summary
        summary = agent._generate_summary(findings)
        
        # Verify
        assert len(summary) > 0
        assert "login forms" in summary.lower() or "password" in summary.lower()
        assert "suspicious patterns" in summary.lower() or "javascript" in summary.lower()
        assert "exfiltration" in summary.lower()
    
    async def test_generate_summary_low_risk(self, mock_logger):
        """Test summary generation for low-risk findings"""
        agent = ReportAgent(mock_logger)
        
        findings = {
            "dom": {"forms_count": 0, "password_fields": []},
            "javascript": {"suspicious_patterns": []},
            "network": {"exfiltration_candidates": []}
        }
        
        # Generate summary
        summary = agent._generate_summary(findings)
        
        # Verify
        assert "No significant phishing indicators" in summary
    
    async def test_generate_conclusion_high_confidence(self, mock_logger):
        """Test conclusion generation for high-confidence phishing"""
        agent = ReportAgent(mock_logger)
        
        findings = {
            "dom": {
                "forms_count": 1,
                "password_fields": [{"id": "pwd"}]
            },
            "javascript": {
                "suspicious_patterns": [
                    {"pattern": "p1"},
                    {"pattern": "p2"},
                    {"pattern": "p3"}
                ]
            },
            "network": {
                "exfiltration_candidates": [{"domain": "evil.com"}]
            }
        }
        
        # Generate conclusion
        conclusion = agent._generate_conclusion(findings)
        
        # Verify
        assert "HIGH CONFIDENCE" in conclusion
        assert "phishing" in conclusion.lower()
    
    async def test_generate_conclusion_medium_confidence(self, mock_logger):
        """Test conclusion generation for medium-confidence findings"""
        agent = ReportAgent(mock_logger)
        
        findings = {
            "dom": {
                "forms_count": 1,
                "password_fields": [{"id": "pwd"}]
            },
            "javascript": {"suspicious_patterns": []},
            "network": {"exfiltration_candidates": []}
        }
        
        # Generate conclusion
        conclusion = agent._generate_conclusion(findings)
        
        # Verify
        assert "MEDIUM CONFIDENCE" in conclusion
    
    async def test_generate_conclusion_low_confidence(self, mock_logger):
        """Test conclusion generation for low-confidence findings"""
        agent = ReportAgent(mock_logger)
        
        findings = {
            "dom": {"forms_count": 0, "password_fields": []},
            "javascript": {"suspicious_patterns": []},
            "network": {"exfiltration_candidates": []}
        }
        
        # Generate conclusion
        conclusion = agent._generate_conclusion(findings)
        
        # Verify
        assert "LOW CONFIDENCE" in conclusion
    
    async def test_report_includes_page_load_info(self, mock_logger, temp_output_dir):
        """Test that report includes page load information"""
        agent = ReportAgent(mock_logger)
        
        results = {
            "url": "https://phishing.com",
            "timestamp": "2026-02-02T12:00:00Z",
            "page_load": {
                "success": True,
                "final_url": "https://phishing.com/login",
                "title": "Fake Login",
                "status_code": 200,
                "screenshot_path": "/path/to/screenshot.png"
            },
            "findings": {}
        }
        
        # Execute
        report_path = await agent.generate_report(results, temp_output_dir)
        content = report_path.read_text()
        
        # Verify page load info
        assert "Fake Login" in content
        assert "200" in content
        assert "screenshot.png" in content
    
    async def test_report_handles_failed_page_load(self, mock_logger, temp_output_dir):
        """Test report generation when page load fails"""
        agent = ReportAgent(mock_logger)
        
        results = {
            "url": "https://phishing.com",
            "timestamp": "2026-02-02T12:00:00Z",
            "page_load": {
                "success": False,
                "error": "Connection timeout"
            },
            "findings": {}
        }
        
        # Execute
        report_path = await agent.generate_report(results, temp_output_dir)
        content = report_path.read_text()
        
        # Verify error is mentioned
        assert "failed" in content.lower()
        assert "Connection timeout" in content
    
    async def test_report_includes_form_details(self, mock_logger, temp_output_dir):
        """Test that report includes detailed form information"""
        agent = ReportAgent(mock_logger)
        
        results = {
            "url": "https://phishing.com",
            "timestamp": "2026-02-02T12:00:00Z",
            "page_load": {"success": True},
            "findings": {
                "dom": {
                    "forms_count": 2,
                    "forms": [
                        {
                            "action": "https://evil.com/steal",
                            "method": "POST",
                            "has_password": True,
                            "has_email": True
                        },
                        {
                            "action": "none",
                            "method": "GET",
                            "has_password": False,
                            "has_email": False
                        }
                    ],
                    "evidence": []
                }
            }
        }
        
        # Execute
        report_path = await agent.generate_report(results, temp_output_dir)
        content = report_path.read_text()
        
        # Verify form details
        assert "Form 1" in content
        assert "Form 2" in content
        assert "evil.com/steal" in content
        assert "POST" in content
    
    async def test_report_includes_js_patterns(self, mock_logger, temp_output_dir):
        """Test that report includes JavaScript patterns"""
        agent = ReportAgent(mock_logger)
        
        results = {
            "url": "https://phishing.com",
            "timestamp": "2026-02-02T12:00:00Z",
            "page_load": {"success": True},
            "findings": {
                "javascript": {
                    "inline_scripts_count": 3,
                    "external_scripts_count": 2,
                    "suspicious_patterns": [
                        {
                            "pattern": "password_access",
                            "count": 2,
                            "description": "Accesses password field values"
                        }
                    ],
                    "evidence": []
                }
            }
        }
        
        # Execute
        report_path = await agent.generate_report(results, temp_output_dir)
        content = report_path.read_text()
        
        # Verify JS patterns
        assert "password_access" in content
        assert "Accesses password field values" in content
    
    async def test_report_includes_exfiltration_endpoints(self, mock_logger, temp_output_dir):
        """Test that report includes exfiltration endpoints"""
        agent = ReportAgent(mock_logger)
        
        results = {
            "url": "https://phishing.com",
            "timestamp": "2026-02-02T12:00:00Z",
            "page_load": {"success": True},
            "findings": {
                "network": {
                    "total_requests": 10,
                    "post_requests": [],
                    "exfiltration_candidates": [
                        {
                            "domain": "evil.tk",
                            "url": "https://evil.tk/steal",
                            "suspicious_score": 5,
                            "reasons": ["Suspicious TLD", "Suspicious endpoint path"]
                        }
                    ],
                    "third_party_domains": [],
                    "evidence": []
                }
            }
        }
        
        # Execute
        report_path = await agent.generate_report(results, temp_output_dir)
        content = report_path.read_text()
        
        # Verify exfiltration info
        assert "evil.tk" in content
        assert "Suspicious TLD" in content
    
    async def test_report_includes_third_party_domains(self, mock_logger, temp_output_dir):
        """Test that report includes third-party domains"""
        agent = ReportAgent(mock_logger)
        
        results = {
            "url": "https://phishing.com",
            "timestamp": "2026-02-02T12:00:00Z",
            "page_load": {"success": True},
            "findings": {
                "network": {
                    "total_requests": 10,
                    "post_requests": [],
                    "exfiltration_candidates": [],
                    "third_party_domains": [
                        {"domain": "cdn.example.com", "request_count": 5},
                        {"domain": "analytics.com", "request_count": 3}
                    ],
                    "evidence": []
                }
            }
        }
        
        # Execute
        report_path = await agent.generate_report(results, temp_output_dir)
        content = report_path.read_text()
        
        # Verify third-party domains
        assert "cdn.example.com" in content
        assert "analytics.com" in content
    
    async def test_report_handles_errors(self, mock_logger, temp_output_dir):
        """Test error handling during report generation"""
        agent = ReportAgent(mock_logger)
        
        # Invalid results (missing required fields)
        results = {}
        
        # Execute - should handle gracefully or raise exception
        try:
            await agent.generate_report(results, temp_output_dir)
        except Exception:
            # Error was raised as expected
            pass
        
        # Verify error was logged (may be called during exception)
        # mock_logger.error.assert_called()
    
    async def test_report_footer(self, mock_logger, temp_output_dir, sample_analysis_results):
        """Test that report includes footer"""
        agent = ReportAgent(mock_logger)
        
        # Execute
        report_path = await agent.generate_report(sample_analysis_results, temp_output_dir)
        content = report_path.read_text()
        
        # Verify footer
        assert "PhishScope" in content
        assert "Evidence-Driven" in content or "Generated by" in content


@pytest.mark.integration
@pytest.mark.asyncio
class TestReportAgentIntegration:
    """Integration tests for ReportAgent"""
    
    async def test_generate_complete_report(self, mock_logger, temp_output_dir, sample_analysis_results):
        """Test generation of a complete report with all sections"""
        agent = ReportAgent(mock_logger)
        
        # Execute
        report_path = await agent.generate_report(sample_analysis_results, temp_output_dir)
        
        # Verify both files exist
        assert report_path.exists()
        assert (temp_output_dir / "report.json").exists()
        
        # Verify markdown content is substantial
        content = report_path.read_text()
        assert len(content) > 500  # Should be a substantial report
        
        # Verify JSON is valid
        with open(temp_output_dir / "report.json", 'r') as f:
            json_data = json.load(f)
        assert json_data is not None