"""
Unit tests for LLMAgent
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from agents.llm_agent import LLMAgent


@pytest.mark.unit
class TestLLMAgent:
    """Test suite for LLMAgent"""
    
    def test_init_watsonx_with_credentials(self, mock_logger):
        """Test WatsonX initialization with credentials"""
        with patch.dict(os.environ, {
            'LLM_PROVIDER': 'watsonx',
            'WATSONX_API_KEY': 'test_key',
            'WATSONX_PROJECT_ID': 'test_project'
        }):
            with patch.object(LLMAgent, '_get_iam_token') as mock_iam:
                mock_iam.return_value = None  # Mock the IAM token method
                agent = LLMAgent(mock_logger)
                agent.iam_token = 'test_token'  # Set token after init
                
                assert agent.provider == 'watsonx'
                assert agent.api_key == 'test_key'
                assert agent.project_id == 'test_project'
    
    def test_init_watsonx_without_credentials(self, mock_logger):
        """Test WatsonX initialization without credentials"""
        with patch.dict(os.environ, {'LLM_PROVIDER': 'watsonx'}, clear=True):
            agent = LLMAgent(mock_logger)
            
            assert agent.enabled is False
            mock_logger.warning.assert_called()
    
    def test_init_rits_with_credentials(self, mock_logger):
        """Test RITS initialization with credentials"""
        with patch.dict(os.environ, {
            'LLM_PROVIDER': 'rits',
            'RITS_API_KEY': 'test_key'
        }):
            with patch.object(LLMAgent, '_test_rits_connection', return_value=True):
                agent = LLMAgent(mock_logger)
                
                assert agent.provider == 'rits'
                assert agent.api_key == 'test_key'
                assert agent.enabled is True
    
    def test_init_rits_without_credentials(self, mock_logger):
        """Test RITS initialization without credentials"""
        with patch.dict(os.environ, {'LLM_PROVIDER': 'rits'}, clear=True):
            agent = LLMAgent(mock_logger)
            
            assert agent.enabled is False
            mock_logger.warning.assert_called()
    
    def test_init_unknown_provider(self, mock_logger):
        """Test initialization with unknown provider"""
        with patch.dict(os.environ, {'LLM_PROVIDER': 'unknown'}):
            agent = LLMAgent(mock_logger)
            
            assert agent.enabled is False
            mock_logger.warning.assert_called()
    
    def test_is_available_when_enabled(self, mock_logger):
        """Test is_available returns True when enabled"""
        with patch.dict(os.environ, {
            'LLM_PROVIDER': 'rits',
            'RITS_API_KEY': 'test_key'
        }):
            with patch.object(LLMAgent, '_test_rits_connection', return_value=True):
                agent = LLMAgent(mock_logger)
                assert agent.is_available() is True
    
    def test_is_available_when_disabled(self, mock_logger):
        """Test is_available returns False when disabled"""
        with patch.dict(os.environ, {'LLM_PROVIDER': 'unknown'}):
            agent = LLMAgent(mock_logger)
            assert agent.is_available() is False
    
    def test_analyze_when_disabled(self, mock_logger):
        """Test analyze returns error when AI is disabled"""
        with patch.dict(os.environ, {'LLM_PROVIDER': 'unknown'}):
            agent = LLMAgent(mock_logger)
            
            findings = {"dom": {}, "javascript": {}, "network": {}}
            result = agent.analyze(findings)
            
            assert result['ai_enabled'] is False
            assert 'error' in result
    
    def test_analyze_with_findings(self, mock_logger, sample_dom_findings, sample_js_findings, sample_network_findings):
        """Test analyze with complete findings"""
        with patch.dict(os.environ, {
            'LLM_PROVIDER': 'rits',
            'RITS_API_KEY': 'test_key'
        }):
            with patch.object(LLMAgent, '_test_rits_connection', return_value=True):
                agent = LLMAgent(mock_logger)
                agent.enabled = True
                
                # Mock LLM responses
                with patch.object(agent, '_generate_text', return_value="VERDICT: High Risk\nCONFIDENCE: 95%"):
                    findings = {
                        'dom': sample_dom_findings,
                        'javascript': sample_js_findings,
                        'network': sample_network_findings
                    }
                    
                    result = agent.analyze(findings)
                    
                    assert result['ai_enabled'] is True
                    assert 'phishing_assessment' in result
                    assert 'attack_analysis' in result
                    assert 'recommendations' in result
    
    def test_prepare_findings_context(self, mock_logger):
        """Test preparation of findings context for prompts"""
        with patch.dict(os.environ, {'LLM_PROVIDER': 'unknown'}):
            agent = LLMAgent(mock_logger)
            
            findings = {
                'dom': {
                    'forms_count': 2,
                    'password_fields': [{'id': 'pwd'}],
                    'hidden_inputs': [{'name': 'token'}]
                },
                'javascript': {
                    'suspicious_patterns': [
                        {'type': 'password_access', 'description': 'Accesses passwords'}
                    ]
                },
                'network': {
                    'exfiltration_candidates': [
                        {'domain': 'evil.com'}
                    ]
                }
            }
            
            context = agent._prepare_findings_context(findings)
            
            assert '2 login form' in context
            assert 'password field' in context
            assert 'hidden input' in context
            assert 'suspicious JavaScript pattern' in context
            assert 'exfiltration endpoint' in context
    
    def test_parse_assessment_response(self, mock_logger):
        """Test parsing of AI assessment response"""
        with patch.dict(os.environ, {'LLM_PROVIDER': 'unknown'}):
            agent = LLMAgent(mock_logger)
            
            response = """
VERDICT: High Risk
CONFIDENCE: 95%
KEY INDICATORS:
- Login form with password field
- JavaScript credential theft
- External data exfiltration
REASONING: This page exhibits multiple phishing indicators.
ATTACK TYPE: Credential harvesting
"""
            
            result = agent._parse_assessment_response(response)
            
            assert result['verdict'] == 'High Risk'
            assert result['confidence'] == 95
            assert len(result['key_indicators']) == 3
            assert 'phishing' in result['reasoning'].lower()
            assert result['attack_type'] == 'Credential harvesting'
    
    def test_parse_attack_analysis(self, mock_logger):
        """Test parsing of attack analysis response"""
        with patch.dict(os.environ, {'LLM_PROVIDER': 'unknown'}):
            agent = LLMAgent(mock_logger)
            
            response = """
ATTACK FLOW:
- User visits phishing page
- Enters credentials
- Data sent to attacker server
TECHNIQUES USED:
- Form spoofing
- JavaScript interception
DATA TARGETED:
- Username
- Password
"""
            
            result = agent._parse_attack_analysis(response)
            
            assert len(result['attack_flow']) == 3
            assert len(result['techniques_used']) == 2
            assert len(result['data_targeted']) == 2
    
    def test_fallback_assessment_high_risk(self, mock_logger):
        """Test fallback assessment for high-risk findings"""
        with patch.dict(os.environ, {'LLM_PROVIDER': 'unknown'}):
            agent = LLMAgent(mock_logger)
            
            findings = {
                'dom': {
                    'forms_count': 1,
                    'password_fields': [{'id': 'pwd'}]
                },
                'javascript': {
                    'suspicious_patterns': [
                        {'pattern': 'p1'},
                        {'pattern': 'p2'}
                    ]
                },
                'network': {
                    'exfiltration_candidates': [{'domain': 'evil.com'}]
                }
            }
            
            result = agent._fallback_assessment(findings)
            
            assert result['verdict'] == 'High Risk'
            assert result['confidence'] >= 60
            assert len(result['key_indicators']) > 0
    
    def test_fallback_assessment_low_risk(self, mock_logger):
        """Test fallback assessment for low-risk findings"""
        with patch.dict(os.environ, {'LLM_PROVIDER': 'unknown'}):
            agent = LLMAgent(mock_logger)
            
            findings = {
                'dom': {'forms_count': 0, 'password_fields': []},
                'javascript': {'suspicious_patterns': []},
                'network': {'exfiltration_candidates': []}
            }
            
            result = agent._fallback_assessment(findings)
            
            assert result['verdict'] == 'Low Risk'
            assert result['confidence'] < 30
    
    def test_fallback_recommendations(self, mock_logger):
        """Test fallback recommendations"""
        with patch.dict(os.environ, {'LLM_PROVIDER': 'unknown'}):
            agent = LLMAgent(mock_logger)
            
            recommendations = agent._fallback_recommendations()
            
            assert len(recommendations) > 0
            assert any('block' in r.lower() for r in recommendations)
            assert any('report' in r.lower() for r in recommendations)
    
    @patch('requests.post')
    def test_generate_text_watsonx_success(self, mock_post, mock_logger):
        """Test WatsonX text generation success"""
        with patch.dict(os.environ, {
            'LLM_PROVIDER': 'watsonx',
            'WATSONX_API_KEY': 'test_key',
            'WATSONX_PROJECT_ID': 'test_project'
        }):
            # Mock IAM token request
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {
                'access_token': 'test_token'
            }
            
            agent = LLMAgent(mock_logger)
            agent.iam_token = 'test_token'
            
            # Mock generation request
            mock_post.return_value.json.return_value = {
                'results': [{'generated_text': 'Test response'}]
            }
            
            result = agent._generate_text_watsonx('Test prompt')
            
            assert result == 'Test response'
    
    @patch('requests.post')
    def test_generate_text_rits_success(self, mock_post, mock_logger):
        """Test RITS text generation success"""
        with patch.dict(os.environ, {
            'LLM_PROVIDER': 'rits',
            'RITS_API_KEY': 'test_key'
        }):
            with patch.object(LLMAgent, '_test_rits_connection', return_value=True):
                agent = LLMAgent(mock_logger)
                
                # Mock generation request
                mock_post.return_value.status_code = 200
                mock_post.return_value.json.return_value = {
                    'choices': [
                        {
                            'message': {
                                'content': 'Test response'
                            }
                        }
                    ]
                }
                
                result = agent._generate_text_rits('Test prompt')
                
                assert result == 'Test response'
    
    @patch('requests.post')
    def test_generate_text_rits_reasoning_content(self, mock_post, mock_logger):
        """Test RITS text generation with reasoning_content field"""
        with patch.dict(os.environ, {
            'LLM_PROVIDER': 'rits',
            'RITS_API_KEY': 'test_key'
        }):
            with patch.object(LLMAgent, '_test_rits_connection', return_value=True):
                agent = LLMAgent(mock_logger)
                
                # Mock generation request with reasoning_content
                mock_post.return_value.status_code = 200
                mock_post.return_value.json.return_value = {
                    'choices': [
                        {
                            'message': {
                                'content': None,
                                'reasoning_content': 'Reasoning response'
                            }
                        }
                    ]
                }
                
                result = agent._generate_text_rits('Test prompt')
                
                assert result == 'Reasoning response'
    
    @patch('requests.post')
    def test_generate_text_error_handling(self, mock_post, mock_logger):
        """Test error handling in text generation"""
        with patch.dict(os.environ, {
            'LLM_PROVIDER': 'watsonx',
            'WATSONX_API_KEY': 'test_key',
            'WATSONX_PROJECT_ID': 'test_project'
        }):
            # Mock IAM token request
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {
                'access_token': 'test_token'
            }
            
            agent = LLMAgent(mock_logger)
            agent.iam_token = 'test_token'
            
            # Mock failed generation request
            mock_post.return_value.status_code = 500
            mock_post.return_value.text = 'Server error'
            
            result = agent._generate_text_watsonx('Test prompt')
            
            assert result is None
            mock_logger.error.assert_called()


@pytest.mark.integration
@pytest.mark.requires_ai
class TestLLMAgentIntegration:
    """Integration tests for LLMAgent (requires actual AI credentials)"""
    
    def test_real_watsonx_analysis(self, mock_logger, sample_dom_findings, sample_js_findings, sample_network_findings):
        """Test real WatsonX analysis (skipped if credentials not available)"""
        if not os.getenv('WATSONX_API_KEY'):
            pytest.skip("WatsonX credentials not available")
        
        agent = LLMAgent(mock_logger)
        
        if not agent.is_available():
            pytest.skip("WatsonX not available")
        
        findings = {
            'dom': sample_dom_findings,
            'javascript': sample_js_findings,
            'network': sample_network_findings
        }
        
        result = agent.analyze(findings)
        
        assert result['ai_enabled'] is True
        assert 'phishing_assessment' in result
    
    def test_real_rits_analysis(self, mock_logger, sample_dom_findings, sample_js_findings, sample_network_findings):
        """Test real RITS analysis (skipped if credentials not available)"""
        if not os.getenv('RITS_API_KEY'):
            pytest.skip("RITS credentials not available")
        
        with patch.dict(os.environ, {'LLM_PROVIDER': 'rits'}):
            agent = LLMAgent(mock_logger)
            
            if not agent.is_available():
                pytest.skip("RITS not available")
            
            findings = {
                'dom': sample_dom_findings,
                'javascript': sample_js_findings,
                'network': sample_network_findings
            }
            
            result = agent.analyze(findings)
            
            assert result['ai_enabled'] is True
            assert 'phishing_assessment' in result