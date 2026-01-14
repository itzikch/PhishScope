"""
LLM Agent for PhishScope
Supports multiple LLM providers: IBM WatsonX and RITS (OpenAI-compatible)
Provider is configured via LLM_PROVIDER environment variable
"""

import os
import json
import requests
from typing import Dict, Any, Optional, List
from logging import Logger


class LLMAgent:
    """
    Multi-provider LLM agent for AI-enhanced phishing analysis.
    
    Supports:
    - IBM WatsonX (watsonx)
    - RITS OpenAI-compatible API (rits)
    
    Provider is selected via LLM_PROVIDER environment variable.
    """
    
    def __init__(self, logger: Logger):
        """Initialize LLM agent with provider-specific configuration"""
        self.logger = logger
        
        # Get provider configuration
        self.provider = os.getenv('LLM_PROVIDER', 'watsonx').lower()
        self.model = os.getenv('LLM_MODEL', '')
        
        # Initialize based on provider
        if self.provider == 'watsonx':
            self._init_watsonx()
        elif self.provider == 'rits':
            self._init_rits()
        else:
            self.logger.warning(f"Unknown LLM provider: {self.provider}. AI features disabled.")
            self.enabled = False
    
    def _init_watsonx(self):
        """Initialize IBM WatsonX provider"""
        self.api_key = os.getenv('WATSONX_API_KEY')
        self.project_id = os.getenv('WATSONX_PROJECT_ID')
        self.url = os.getenv('WATSONX_URL', 'https://us-south.ml.cloud.ibm.com')
        self.model_id = os.getenv('WATSONX_MODEL_ID', 'ibm/granite-3-8b-instruct')
        
        if not self.api_key or not self.project_id:
            self.logger.warning("WatsonX credentials not found. AI features disabled.")
            self.enabled = False
            self.iam_token = None
            return
        
        self.logger.info("WatsonX Configuration:")
        self.logger.info(f"  Provider: IBM watsonx.ai")
        self.logger.info(f"  Model: {self.model_id}")
        self.logger.info(f"  URL: {self.url}")
        
        # Get IAM token
        self._get_iam_token()
        self.enabled = self.iam_token is not None
    
    def _init_rits(self):
        """Initialize RITS OpenAI-compatible provider"""
        self.api_key = os.getenv('RITS_API_KEY')
        self.api_base_url = os.getenv('RITS_API_BASE_URL', 'http://9.46.81.185:4000')
        self.model_id = self.model or os.getenv('LLM_MODEL', 'rits/openai/gpt-oss-120b')
        
        if not self.api_key:
            self.logger.warning("RITS API key not found. AI features disabled.")
            self.enabled = False
            return
        
        self.logger.info("RITS Configuration:")
        self.logger.info(f"  Provider: RITS (OpenAI-compatible)")
        self.logger.info(f"  Model: {self.model_id}")
        self.logger.info(f"  Base URL: {self.api_base_url}")
        
        # Test connection
        self.enabled = self._test_rits_connection()
    
    def _get_iam_token(self):
        """Get IBM Cloud IAM token for WatsonX"""
        try:
            self.logger.info("Getting IAM token from IBM Cloud...")
            
            response = requests.post(
                'https://iam.cloud.ibm.com/identity/token',
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                data={
                    'grant_type': 'urn:ibm:params:oauth:grant-type:apikey',
                    'apikey': self.api_key
                },
                timeout=10
            )
            
            if response.status_code == 200:
                self.iam_token = response.json()['access_token']
                self.logger.info("✓ WatsonX AI initialized successfully (REST API)")
            else:
                self.logger.error(f"Failed to get IAM token: {response.status_code} - {response.text}")
                self.iam_token = None
                
        except Exception as e:
            self.logger.error(f"Failed to get IAM token: {str(e)}")
            self.iam_token = None
    
    def _test_rits_connection(self) -> bool:
        """Test RITS API connection"""
        try:
            # Simple test to verify API is accessible
            self.logger.info("Testing RITS API connection...")
            response = requests.get(
                f"{self.api_base_url}/v1/models",
                headers={'Authorization': f'Bearer {self.api_key}'},
                timeout=5
            )
            
            if response.status_code == 200:
                self.logger.info("✓ RITS API initialized successfully")
                return True
            else:
                self.logger.warning(f"RITS API test failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.warning(f"RITS API connection test failed: {str(e)}")
            return False
    
    def _generate_text_watsonx(self, prompt: str, max_tokens: int = 800, temperature: float = 0.5) -> Optional[str]:
        """Generate text using WatsonX REST API"""
        
        if not self.iam_token:
            return None
        
        try:
            url = f"{self.url}/ml/v1/text/generation?version=2023-05-29"
            
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': f'Bearer {self.iam_token}'
            }
            
            body = {
                'input': prompt,
                'parameters': {
                    'max_new_tokens': max_tokens,
                    'temperature': temperature,
                    'top_p': 0.9,
                    'top_k': 50
                },
                'model_id': self.model_id,
                'project_id': self.project_id
            }
            
            response = requests.post(url, headers=headers, json=body, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                return result['results'][0]['generated_text'].strip()
            else:
                self.logger.error(f"WatsonX API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error generating text with WatsonX: {str(e)}")
            return None
    
    def _generate_text_rits(self, prompt: str, max_tokens: int = 800, temperature: float = 0.5) -> Optional[str]:
        """Generate text using RITS OpenAI-compatible API"""
        
        try:
            url = f"{self.api_base_url}/v1/chat/completions"
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.api_key}'
            }
            
            body = {
                'model': self.model_id,
                'messages': [
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                'max_tokens': max_tokens,
                'temperature': temperature,
                'top_p': 0.9
            }
            
            response = requests.post(url, headers=headers, json=body, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                message = result.get('choices', [{}])[0].get('message', {})
                
                # Try standard content field first
                content = message.get('content')
                
                # If content is None, try reasoning_content (for reasoning models)
                if content is None:
                    content = message.get('reasoning_content')
                
                # If still None, try provider_specific_fields
                if content is None:
                    provider_fields = message.get('provider_specific_fields', {})
                    content = provider_fields.get('reasoning_content') or provider_fields.get('reasoning')
                
                if content:
                    return content.strip()
                else:
                    self.logger.error(f"RITS API returned empty content: {result}")
                    return None
            else:
                self.logger.error(f"RITS API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error generating text with RITS: {str(e)}")
            return None
    
    def _generate_text(self, prompt: str, max_tokens: int = 800, temperature: float = 0.5) -> Optional[str]:
        """Generate text using configured provider"""
        if self.provider == 'watsonx':
            return self._generate_text_watsonx(prompt, max_tokens, temperature)
        elif self.provider == 'rits':
            return self._generate_text_rits(prompt, max_tokens, temperature)
        else:
            return None
    
    def is_available(self) -> bool:
        """Check if AI analysis is available"""
        return self.enabled
    
    def analyze(self, findings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform AI-enhanced analysis of phishing findings
        
        Args:
            findings: Dictionary containing DOM, JS, and network findings
            
        Returns:
            Dictionary with AI analysis results
        """
        if not self.is_available():
            return {
                'ai_enabled': False,
                'error': 'AI analysis not available'
            }
        
        self.logger.info("Starting LLM AI analysis...")
        
        try:
            # Perform different types of analysis
            phishing_assessment = self._assess_phishing_likelihood(findings)
            attack_analysis = self._analyze_attack_methodology(findings)
            recommendations = self._generate_recommendations(findings, phishing_assessment)
            
            self.logger.info("✓ LLM AI analysis complete")
            
            return {
                'ai_enabled': True,
                'provider': self.provider,
                'model': self.model_id,
                'phishing_assessment': phishing_assessment,
                'attack_analysis': attack_analysis,
                'threat_intelligence': {},
                'recommendations': recommendations
            }
            
        except Exception as e:
            self.logger.error(f"AI analysis failed: {str(e)}")
            return {
                'ai_enabled': True,
                'error': str(e)
            }
    
    def _assess_phishing_likelihood(self, findings: Dict[str, Any]) -> Dict[str, Any]:
        """Use AI to assess phishing likelihood"""
        
        # Prepare context from findings
        context = self._prepare_findings_context(findings)
        
        prompt = f"""You are a cybersecurity expert analyzing a potentially malicious webpage.

FINDINGS:
{context}

Based on these findings, provide a phishing risk assessment in the following format:

VERDICT: [High Risk/Medium Risk/Low Risk]
CONFIDENCE: [0-100]%
KEY INDICATORS:
- [List 3-5 key indicators that support your verdict]

REASONING: [2-3 sentences explaining your assessment]

ATTACK TYPE: [Describe the type of phishing attack if applicable]"""

        response = self._generate_text(prompt, max_tokens=500)
        
        if not response:
            return self._fallback_assessment(findings)
        
        # Parse the response
        return self._parse_assessment_response(response)
    
    def _analyze_attack_methodology(self, findings: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the attack methodology using AI"""
        
        context = self._prepare_findings_context(findings)
        
        prompt = f"""You are a threat intelligence analyst. Analyze this phishing attack methodology.

FINDINGS:
{context}

Provide a detailed attack analysis:

ATTACK FLOW:
[Step-by-step description of how the attack works]

TECHNIQUES USED:
[List specific techniques]

DATA TARGETED:
[What data is the attacker trying to steal]"""

        response = self._generate_text(prompt, max_tokens=800)
        
        if not response:
            return {'error': 'Failed to generate attack analysis'}
        
        return self._parse_attack_analysis(response)
    
    def _generate_recommendations(self, findings: Dict[str, Any], assessment: Dict[str, Any]) -> List[str]:
        """Generate security recommendations using AI"""
        
        verdict = assessment.get('verdict', 'Unknown')
        context = self._prepare_findings_context(findings)
        
        prompt = f"""You are a security consultant. The phishing risk assessment is: {verdict}

FINDINGS:
{context}

Provide 5-7 actionable security recommendations for:
1. Immediate response actions
2. Detection and monitoring
3. User education

Format as a bullet list."""

        response = self._generate_text(prompt, max_tokens=400)
        
        if not response:
            return self._fallback_recommendations()
        
        # Parse recommendations
        recommendations = []
        for line in response.split('\n'):
            line = line.strip()
            if line and (line.startswith('-') or line.startswith('•') or line[0].isdigit()):
                recommendations.append(line.lstrip('-•0123456789. '))
        
        return recommendations if recommendations else self._fallback_recommendations()
    
    def _prepare_findings_context(self, findings: Dict[str, Any]) -> str:
        """Prepare findings as context for AI prompts"""
        
        context_parts = []
        
        # DOM findings
        dom = findings.get('dom', {})
        if dom.get('forms_count', 0) > 0:
            context_parts.append(f"- {dom['forms_count']} login form(s) detected")
        if dom.get('password_fields'):
            context_parts.append(f"- {len(dom['password_fields'])} password field(s)")
        if dom.get('hidden_inputs'):
            context_parts.append(f"- {len(dom['hidden_inputs'])} hidden input(s)")
        
        # JavaScript findings
        js = findings.get('javascript', {})
        if js.get('suspicious_patterns'):
            context_parts.append(f"- {len(js['suspicious_patterns'])} suspicious JavaScript pattern(s)")
            for pattern in js['suspicious_patterns'][:3]:
                context_parts.append(f"  • {pattern.get('type', 'unknown')}: {pattern.get('description', '')}")
        
        # Network findings
        network = findings.get('network', {})
        if network.get('exfiltration_candidates'):
            context_parts.append(f"- {len(network['exfiltration_candidates'])} potential data exfiltration endpoint(s)")
        
        return '\n'.join(context_parts) if context_parts else "No significant findings detected"
    
    def _parse_assessment_response(self, response: str) -> Dict[str, Any]:
        """Parse AI assessment response"""
        
        result = {
            'verdict': 'Unknown',
            'confidence': 50,
            'key_indicators': [],
            'reasoning': '',
            'attack_type': '',
            'full_response': response
        }
        
        lines = response.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            
            # Handle both plain and markdown formatted responses
            if 'VERDICT:' in line:
                result['verdict'] = line.split('VERDICT:')[-1].replace('**', '').strip()
            elif 'CONFIDENCE:' in line:
                conf_str = line.split('CONFIDENCE:')[-1].replace('**', '').strip().rstrip('%')
                try:
                    result['confidence'] = int(conf_str)
                except:
                    pass
            elif 'KEY INDICATORS:' in line:
                current_section = 'indicators'
            elif 'REASONING:' in line:
                current_section = 'reasoning'
                result['reasoning'] = line.split('REASONING:')[-1].replace('**', '').strip()
            elif 'ATTACK TYPE:' in line:
                result['attack_type'] = line.split('ATTACK TYPE:')[-1].replace('**', '').strip()
            elif current_section == 'indicators' and line.startswith('-'):
                result['key_indicators'].append(line.lstrip('- '))
            elif current_section == 'reasoning' and line and not any(x in line for x in ['VERDICT:', 'CONFIDENCE:', 'KEY INDICATORS:', 'ATTACK TYPE:']):
                result['reasoning'] += ' ' + line
        
        return result
    
    def _parse_attack_analysis(self, response: str) -> Dict[str, Any]:
        """Parse attack analysis response"""
        
        result = {
            'attack_flow': [],
            'techniques_used': [],
            'data_targeted': [],
            'full_analysis': response
        }
        
        lines = response.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            
            if 'ATTACK FLOW:' in line:
                current_section = 'flow'
            elif 'TECHNIQUES USED:' in line:
                current_section = 'techniques'
            elif 'DATA TARGETED:' in line:
                current_section = 'data'
            elif line and (line.startswith('-') or line.startswith('•') or line[0].isdigit()):
                cleaned = line.lstrip('-•0123456789. ')
                if current_section == 'flow':
                    result['attack_flow'].append(cleaned)
                elif current_section == 'techniques':
                    result['techniques_used'].append(cleaned)
                elif current_section == 'data':
                    result['data_targeted'].append(cleaned)
        
        return result
    
    def _fallback_assessment(self, findings: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback assessment when AI is unavailable"""
        
        # Simple rule-based assessment
        risk_score = 0
        indicators = []
        
        dom = findings.get('dom', {})
        js = findings.get('javascript', {})
        network = findings.get('network', {})
        
        if dom.get('forms_count', 0) > 0:
            risk_score += 30
            indicators.append("Login form detected")
        
        if dom.get('password_fields'):
            risk_score += 25
            indicators.append("Password fields present")
        
        if js.get('suspicious_patterns'):
            risk_score += 20
            indicators.append(f"{len(js['suspicious_patterns'])} suspicious JS patterns")
        
        if network.get('exfiltration_candidates'):
            risk_score += 25
            indicators.append("Potential data exfiltration endpoints")
        
        if risk_score >= 60:
            verdict = "High Risk"
        elif risk_score >= 30:
            verdict = "Medium Risk"
        else:
            verdict = "Low Risk"
        
        return {
            'verdict': verdict,
            'confidence': min(risk_score, 95),
            'key_indicators': indicators if indicators else ["No significant indicators"],
            'reasoning': f"Rule-based assessment (AI unavailable). Risk score: {risk_score}/100",
            'attack_type': 'Credential phishing' if risk_score >= 50 else 'Unknown'
        }
    
    def _fallback_recommendations(self) -> List[str]:
        """Fallback recommendations when AI is unavailable"""
        return [
            "Block access to this URL immediately",
            "Report to security team for investigation",
            "Scan affected systems for malware",
            "Reset credentials if exposed",
            "Monitor for suspicious activity",
            "Educate users about phishing indicators"
        ]

# Made with Bob
