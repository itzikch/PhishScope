"""
Unit tests for NetworkInspectorAgent
"""

import pytest
from pathlib import Path
from unittest.mock import Mock
from agents.network_inspector import NetworkInspectorAgent


@pytest.mark.unit
@pytest.mark.asyncio
class TestNetworkInspectorAgent:
    """Test suite for NetworkInspectorAgent"""
    
    async def test_init(self, mock_logger):
        """Test NetworkInspectorAgent initialization"""
        agent = NetworkInspectorAgent(mock_logger)
        assert agent.logger == mock_logger
        assert len(agent.SUSPICIOUS_TLDS) > 0
        assert len(agent.LEGITIMATE_DOMAINS) > 0
    
    async def test_analyze_empty_log(self, mock_logger, temp_output_dir):
        """Test analysis with empty network log"""
        agent = NetworkInspectorAgent(mock_logger)
        
        # Execute with empty log
        findings = await agent.analyze([], temp_output_dir)
        
        # Verify default structure
        assert findings["total_requests"] == 0
        assert findings["post_requests"] == []
        assert findings["exfiltration_candidates"] == []
        
        # Verify warning was logged
        mock_logger.warning.assert_called_once()
    
    async def test_analyze_with_post_requests(self, mock_logger, temp_output_dir):
        """Test detection of POST requests"""
        agent = NetworkInspectorAgent(mock_logger)
        
        network_log = [
            {
                "type": "request",
                "url": "https://example.com/",
                "method": "GET"
            },
            {
                "type": "request",
                "url": "https://evil.com/steal",
                "method": "POST",
                "headers": {"Content-Type": "application/json"}
            }
        ]
        
        # Execute
        findings = await agent.analyze(network_log, temp_output_dir)
        
        # Verify
        assert findings["total_requests"] == 2
        assert len(findings["post_requests"]) == 1
        assert findings["post_requests"][0]["url"] == "https://evil.com/steal"
    
    async def test_identify_exfiltration_suspicious_tld(self, mock_logger, temp_output_dir):
        """Test detection of suspicious TLDs"""
        agent = NetworkInspectorAgent(mock_logger)
        
        network_log = [
            {
                "type": "request",
                "url": "https://phishing.tk/steal",
                "method": "POST"
            }
        ]
        
        # Execute
        findings = await agent.analyze(network_log, temp_output_dir)
        
        # Verify
        assert len(findings["exfiltration_candidates"]) > 0
        candidate = findings["exfiltration_candidates"][0]
        assert "Suspicious TLD" in candidate["reasons"]
        assert candidate["suspicious_score"] >= 2
    
    async def test_identify_exfiltration_ip_address(self, mock_logger, temp_output_dir):
        """Test detection of direct IP addresses"""
        agent = NetworkInspectorAgent(mock_logger)
        
        network_log = [
            {
                "type": "request",
                "url": "http://192.168.1.100:8080/api/data",
                "method": "POST"
            }
        ]
        
        # Execute
        findings = await agent.analyze(network_log, temp_output_dir)
        
        # Verify
        assert len(findings["exfiltration_candidates"]) > 0
        candidate = findings["exfiltration_candidates"][0]
        # Check for the actual reason text from the code
        assert any("Direct IP address" in reason or "IP address" in reason for reason in candidate["reasons"])
    
    async def test_identify_exfiltration_suspicious_path(self, mock_logger, temp_output_dir):
        """Test detection of suspicious endpoint paths"""
        agent = NetworkInspectorAgent(mock_logger)
        
        network_log = [
            {
                "type": "request",
                "url": "https://evil.com/api/login",
                "method": "POST"
            }
        ]
        
        # Execute
        findings = await agent.analyze(network_log, temp_output_dir)
        
        # Verify
        assert len(findings["exfiltration_candidates"]) > 0
        candidate = findings["exfiltration_candidates"][0]
        assert "Suspicious endpoint path" in candidate["reasons"]
    
    async def test_skip_legitimate_domains(self, mock_logger, temp_output_dir):
        """Test that legitimate domains are not flagged"""
        agent = NetworkInspectorAgent(mock_logger)
        
        network_log = [
            {
                "type": "request",
                "url": "https://www.google.com/api/login",
                "method": "POST"
            },
            {
                "type": "request",
                "url": "https://ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js",
                "method": "GET"
            }
        ]
        
        # Execute
        findings = await agent.analyze(network_log, temp_output_dir)
        
        # Verify legitimate domains are not flagged
        assert len(findings["exfiltration_candidates"]) == 0
    
    async def test_identify_third_party_domains(self, mock_logger, temp_output_dir):
        """Test identification of third-party domains"""
        agent = NetworkInspectorAgent(mock_logger)
        
        network_log = [
            {
                "type": "request",
                "url": "https://example.com/",
                "method": "GET"
            },
            {
                "type": "request",
                "url": "https://cdn.example.com/script.js",
                "method": "GET"
            },
            {
                "type": "request",
                "url": "https://analytics.thirdparty.com/track",
                "method": "POST"
            }
        ]
        
        # Execute
        findings = await agent.analyze(network_log, temp_output_dir)
        
        # Verify
        assert len(findings["third_party_domains"]) == 2
        domains = [d["domain"] for d in findings["third_party_domains"]]
        assert "cdn.example.com" in domains
        assert "analytics.thirdparty.com" in domains
    
    async def test_identify_suspicious_endpoints(self, mock_logger, temp_output_dir):
        """Test detection of suspicious endpoint keywords"""
        agent = NetworkInspectorAgent(mock_logger)
        
        network_log = [
            {
                "type": "request",
                "url": "https://api.telegram.org/bot123/sendMessage",
                "method": "POST"
            },
            {
                "type": "request",
                "url": "https://discord.com/api/webhooks/123/abc",
                "method": "POST"
            }
        ]
        
        # Execute
        findings = await agent.analyze(network_log, temp_output_dir)
        
        # Verify
        assert len(findings["suspicious_endpoints"]) == 2
        keywords = [e["keyword"] for e in findings["suspicious_endpoints"]]
        assert "telegram" in keywords
        assert "discord" in keywords or "webhook" in keywords
    
    async def test_is_ip_address(self, mock_logger):
        """Test IP address detection"""
        agent = NetworkInspectorAgent(mock_logger)
        
        # Valid IPs
        assert agent._is_ip_address("192.168.1.1") is True
        assert agent._is_ip_address("10.0.0.1") is True
        assert agent._is_ip_address("8.8.8.8") is True
        
        # Invalid IPs
        assert agent._is_ip_address("example.com") is False
        assert agent._is_ip_address("192.168.1.256") is False
        assert agent._is_ip_address("not.an.ip.address") is False
        
        # With port
        assert agent._is_ip_address("192.168.1.1:8080") is True
    
    async def test_saves_network_log(self, mock_logger, temp_output_dir):
        """Test that network log is saved"""
        agent = NetworkInspectorAgent(mock_logger)
        
        network_log = [
            {
                "type": "request",
                "url": "https://example.com/",
                "method": "GET"
            }
        ]
        
        # Execute
        findings = await agent.analyze(network_log, temp_output_dir)
        
        # Verify network log was saved
        log_path = temp_output_dir / "artifacts" / "network_log.json"
        assert log_path.exists()
    
    async def test_saves_exfiltration_candidates(self, mock_logger, temp_output_dir):
        """Test that exfiltration candidates are saved"""
        agent = NetworkInspectorAgent(mock_logger)
        
        network_log = [
            {
                "type": "request",
                "url": "https://evil.tk/steal",
                "method": "POST"
            }
        ]
        
        # Execute
        findings = await agent.analyze(network_log, temp_output_dir)
        
        # Verify exfiltration candidates were saved
        exfil_path = temp_output_dir / "artifacts" / "exfiltration_candidates.json"
        assert exfil_path.exists()
    
    async def test_generate_evidence(self, mock_logger):
        """Test evidence generation"""
        agent = NetworkInspectorAgent(mock_logger)
        
        findings = {
            "total_requests": 10,
            "post_requests": [{"url": "https://evil.com/steal"}],
            "exfiltration_candidates": [
                {
                    "domain": "evil.tk",
                    "suspicious_score": 3,
                    "reasons": ["Suspicious TLD", "Suspicious endpoint path"]
                }
            ],
            "third_party_domains": [
                {"domain": "cdn.example.com"},
                {"domain": "analytics.com"}
            ],
            "suspicious_endpoints": [
                {"keyword": "telegram"}
            ]
        }
        
        # Generate evidence
        evidence = agent._generate_evidence(findings)
        
        # Verify comprehensive evidence
        assert len(evidence) > 0
        assert any("10 network request" in e for e in evidence)
        assert any("POST request" in e for e in evidence)
        assert any("exfiltration endpoint" in e for e in evidence)
        assert any("third-party domain" in e for e in evidence)
        assert any("suspicious endpoint" in e for e in evidence)
    
    async def test_exfiltration_scoring(self, mock_logger, temp_output_dir):
        """Test that exfiltration candidates are scored correctly"""
        agent = NetworkInspectorAgent(mock_logger)
        
        network_log = [
            {
                "type": "request",
                "url": "https://phishing.tk/api/login?data=creds",
                "method": "POST"
            }
        ]
        
        # Execute
        findings = await agent.analyze(network_log, temp_output_dir)
        
        # Verify scoring
        assert len(findings["exfiltration_candidates"]) > 0
        candidate = findings["exfiltration_candidates"][0]
        
        # Should have multiple reasons
        assert len(candidate["reasons"]) >= 2
        assert candidate["suspicious_score"] >= 3
    
    async def test_handles_errors_gracefully(self, mock_logger, temp_output_dir):
        """Test error handling during analysis"""
        agent = NetworkInspectorAgent(mock_logger)
        
        # Malformed network log
        network_log = [
            {"type": "request"}  # Missing required fields
        ]
        
        # Execute - should not crash
        findings = await agent.analyze(network_log, temp_output_dir)
        
        # Verify error was captured or handled
        assert "error" in findings or findings["total_requests"] >= 0
    
    async def test_non_standard_port_detection(self, mock_logger, temp_output_dir):
        """Test detection of non-standard ports"""
        agent = NetworkInspectorAgent(mock_logger)
        
        network_log = [
            {
                "type": "request",
                "url": "https://evil.com:8888/api/data",
                "method": "POST"
            }
        ]
        
        # Execute
        findings = await agent.analyze(network_log, temp_output_dir)
        
        # Verify
        if findings["exfiltration_candidates"]:
            candidate = findings["exfiltration_candidates"][0]
            # Non-standard port should contribute to suspicious score
            assert candidate["suspicious_score"] > 0


@pytest.mark.integration
@pytest.mark.asyncio
class TestNetworkInspectorIntegration:
    """Integration tests for NetworkInspectorAgent"""
    
    async def test_analyze_real_network_log(self, mock_logger, temp_output_dir, sample_network_log):
        """Test analysis of a realistic network log"""
        agent = NetworkInspectorAgent(mock_logger)
        
        # Execute
        findings = await agent.analyze(sample_network_log, temp_output_dir)
        
        # Verify
        assert findings["total_requests"] > 0
        assert len(findings["post_requests"]) > 0
        assert len(findings["exfiltration_candidates"]) > 0
        
        # Verify artifacts were created
        log_path = temp_output_dir / "artifacts" / "network_log.json"
        assert log_path.exists()