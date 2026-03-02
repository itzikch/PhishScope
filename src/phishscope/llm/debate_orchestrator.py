"""
Debate Orchestrator for Multi-Agent Phishing Analysis.

This module orchestrates the adversarial debate between three AI agents:
- Prosecutor (argues site IS phishing)
- Defense Attorney (argues site IS legitimate)  
- Judge (makes final ruling)
"""

import logging
import re
from typing import Dict, Any, Optional, AsyncGenerator
from enum import Enum

from phishscope.llm.prompts.debate_prompts import (
    build_intelligence_report,
    get_prosecutor_round1_prompt,
    get_defense_round1_prompt,
    get_prosecutor_round2_prompt,
    get_defense_round2_prompt,
    get_judge_prompt,
)


logger = logging.getLogger(__name__)


class AgentRole(str, Enum):
    """Agent roles in the debate."""
    PROSECUTOR = "prosecutor"
    DEFENSE = "defense"
    JUDGE = "judge"


class DebateRound(str, Enum):
    """Debate round identifiers."""
    PROSECUTOR_R1 = "prosecutor_r1"
    DEFENSE_R1 = "defense_r1"
    PROSECUTOR_R2 = "prosecutor_r2"
    DEFENSE_R2 = "defense_r2"
    JUDGE_RULING = "judge_ruling"


class DebateOrchestrator:
    """
    Orchestrates the multi-agent debate for phishing analysis.
    
    The debate follows this structure:
    1. Build intelligence report from analysis findings
    2. Prosecutor Round 1 - Opening arguments
    3. Defense Round 1 - Opening arguments (sees prosecutor's)
    4. Prosecutor Round 2 - Rebuttal
    5. Defense Round 2 - Rebuttal
    6. Judge - Final ruling (sees full transcript)
    """
    
    def __init__(self, llm_client):
        """
        Initialize debate orchestrator.
        
        Args:
            llm_client: LLM client for making AI calls (must have ainvoke method)
        """
        self.llm_client = llm_client
        
    async def run_debate(
        self,
        url: str,
        page_load: Dict[str, Any],
        dom_findings: Dict[str, Any],
        js_findings: Dict[str, Any],
        network_findings: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Run the complete debate and return results.
        
        Args:
            url: Target URL
            page_load: Page loading results
            dom_findings: DOM analysis results
            js_findings: JavaScript analysis results
            network_findings: Network analysis results
            
        Returns:
            Dictionary containing debate transcript and final verdict
        """
        logger.info("Starting multi-agent debate analysis")
        
        # Build intelligence report
        intelligence_report = build_intelligence_report(
            url, page_load, dom_findings, js_findings, network_findings
        )
        
        debate_transcript = {
            "intelligence_report": intelligence_report,
            "prosecutor_r1": None,
            "defense_r1": None,
            "prosecutor_r2": None,
            "defense_r2": None,
            "judge_ruling": None,
        }
        
        try:
            # Round 1: Prosecutor
            logger.info("[Debate 1/5] Prosecutor Round 1")
            prosecutor_r1_prompt = get_prosecutor_round1_prompt(intelligence_report)
            prosecutor_r1_response = await self.llm_client.ainvoke(prosecutor_r1_prompt)
            debate_transcript["prosecutor_r1"] = self._extract_content(prosecutor_r1_response)
            
            # Round 2: Defense
            logger.info("[Debate 2/5] Defense Round 1")
            defense_r1_prompt = get_defense_round1_prompt(
                intelligence_report,
                debate_transcript["prosecutor_r1"]
            )
            defense_r1_response = await self.llm_client.ainvoke(defense_r1_prompt)
            debate_transcript["defense_r1"] = self._extract_content(defense_r1_response)
            
            # Round 3: Prosecutor Rebuttal
            logger.info("[Debate 3/5] Prosecutor Round 2 (Rebuttal)")
            prosecutor_r2_prompt = get_prosecutor_round2_prompt(
                intelligence_report,
                debate_transcript["prosecutor_r1"],
                debate_transcript["defense_r1"]
            )
            prosecutor_r2_response = await self.llm_client.ainvoke(prosecutor_r2_prompt)
            debate_transcript["prosecutor_r2"] = self._extract_content(prosecutor_r2_response)
            
            # Round 4: Defense Rebuttal
            logger.info("[Debate 4/5] Defense Round 2 (Rebuttal)")
            defense_r2_prompt = get_defense_round2_prompt(
                intelligence_report,
                debate_transcript["prosecutor_r1"],
                debate_transcript["defense_r1"],
                debate_transcript["prosecutor_r2"]
            )
            defense_r2_response = await self.llm_client.ainvoke(defense_r2_prompt)
            debate_transcript["defense_r2"] = self._extract_content(defense_r2_response)
            
            # Round 5: Judge
            logger.info("[Debate 5/5] Judge's Final Ruling")
            judge_prompt = get_judge_prompt(
                intelligence_report,
                debate_transcript["prosecutor_r1"],
                debate_transcript["defense_r1"],
                debate_transcript["prosecutor_r2"],
                debate_transcript["defense_r2"]
            )
            judge_response = await self.llm_client.ainvoke(judge_prompt)
            debate_transcript["judge_ruling"] = self._extract_content(judge_response)
            
            # Parse judge's verdict
            verdict_data = self._parse_judge_verdict(debate_transcript["judge_ruling"])
            
            logger.info(f"Debate complete. Verdict: {verdict_data['verdict']}")
            
            return {
                "debate_enabled": True,
                "debate_transcript": debate_transcript,
                "phishing_assessment": verdict_data,
            }
            
        except Exception as e:
            logger.error(f"Debate failed: {e}", exc_info=True)
            return {
                "debate_enabled": True,
                "debate_transcript": debate_transcript,
                "error": str(e),
                "phishing_assessment": {
                    "verdict": "Error",
                    "confidence": 0,
                    "risk_score": 0,
                    "reasoning": f"Debate analysis failed: {str(e)}",
                }
            }
    
    async def run_debate_streaming(
        self,
        url: str,
        page_load: Dict[str, Any],
        dom_findings: Dict[str, Any],
        js_findings: Dict[str, Any],
        network_findings: Dict[str, Any],
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Run debate with streaming updates for real-time UI.
        
        Yields events as each agent responds:
        - {"event": "scrape_done", "data": {...}}
        - {"event": "agent", "data": {"role": "prosecutor", "round": 1, "content": "..."}}
        - {"event": "verdict", "data": {...}}
        - {"event": "done"}
        
        Args:
            url: Target URL
            page_load: Page loading results
            dom_findings: DOM analysis results
            js_findings: JavaScript analysis results
            network_findings: Network analysis results
            
        Yields:
            Event dictionaries for SSE streaming
        """
        logger.info("Starting streaming debate analysis")
        
        # Build intelligence report
        intelligence_report = build_intelligence_report(
            url, page_load, dom_findings, js_findings, network_findings
        )
        
        # Emit scrape done event
        yield {
            "event": "scrape_done",
            "data": {
                "url": url,
                "final_url": page_load.get("final_url"),
                "title": page_load.get("title"),
                "ssl": page_load.get("ssl"),
                "forms_count": dom_findings.get("forms_count", 0),
                "suspicious_indicators": self._extract_suspicious_indicators(
                    page_load, dom_findings, js_findings, network_findings
                ),
            }
        }
        
        debate_transcript = {}
        
        try:
            # Round 1: Prosecutor
            prosecutor_r1_prompt = get_prosecutor_round1_prompt(intelligence_report)
            prosecutor_r1_response = await self.llm_client.ainvoke(prosecutor_r1_prompt)
            prosecutor_r1_content = self._extract_content(prosecutor_r1_response)
            debate_transcript["prosecutor_r1"] = prosecutor_r1_content
            
            yield {
                "event": "agent",
                "data": {
                    "role": AgentRole.PROSECUTOR,
                    "round": 1,
                    "content": prosecutor_r1_content,
                }
            }
            
            # Round 2: Defense
            defense_r1_prompt = get_defense_round1_prompt(
                intelligence_report, prosecutor_r1_content
            )
            defense_r1_response = await self.llm_client.ainvoke(defense_r1_prompt)
            defense_r1_content = self._extract_content(defense_r1_response)
            debate_transcript["defense_r1"] = defense_r1_content
            
            yield {
                "event": "agent",
                "data": {
                    "role": AgentRole.DEFENSE,
                    "round": 1,
                    "content": defense_r1_content,
                }
            }
            
            # Round 3: Prosecutor Rebuttal
            prosecutor_r2_prompt = get_prosecutor_round2_prompt(
                intelligence_report, prosecutor_r1_content, defense_r1_content
            )
            prosecutor_r2_response = await self.llm_client.ainvoke(prosecutor_r2_prompt)
            prosecutor_r2_content = self._extract_content(prosecutor_r2_response)
            debate_transcript["prosecutor_r2"] = prosecutor_r2_content
            
            yield {
                "event": "agent",
                "data": {
                    "role": AgentRole.PROSECUTOR,
                    "round": 2,
                    "content": prosecutor_r2_content,
                }
            }
            
            # Round 4: Defense Rebuttal
            defense_r2_prompt = get_defense_round2_prompt(
                intelligence_report,
                prosecutor_r1_content,
                defense_r1_content,
                prosecutor_r2_content
            )
            defense_r2_response = await self.llm_client.ainvoke(defense_r2_prompt)
            defense_r2_content = self._extract_content(defense_r2_response)
            debate_transcript["defense_r2"] = defense_r2_content
            
            yield {
                "event": "agent",
                "data": {
                    "role": AgentRole.DEFENSE,
                    "round": 2,
                    "content": defense_r2_content,
                }
            }
            
            # Round 5: Judge
            judge_prompt = get_judge_prompt(
                intelligence_report,
                prosecutor_r1_content,
                defense_r1_content,
                prosecutor_r2_content,
                defense_r2_content
            )
            judge_response = await self.llm_client.ainvoke(judge_prompt)
            judge_content = self._extract_content(judge_response)
            debate_transcript["judge_ruling"] = judge_content
            
            yield {
                "event": "agent",
                "data": {
                    "role": AgentRole.JUDGE,
                    "round": 0,
                    "content": judge_content,
                }
            }
            
            # Parse and emit verdict
            verdict_data = self._parse_judge_verdict(judge_content)
            yield {
                "event": "verdict",
                "data": verdict_data
            }
            
            # Done
            yield {"event": "done"}
            
        except Exception as e:
            logger.error(f"Streaming debate failed: {e}", exc_info=True)
            yield {
                "event": "error",
                "data": {"message": str(e)}
            }
    
    def _extract_content(self, response) -> str:
        """Extract text content from LLM response."""
        if hasattr(response, 'content'):
            return response.content
        return str(response)
    
    def _extract_suspicious_indicators(
        self,
        page_load: Dict[str, Any],
        dom_findings: Dict[str, Any],
        js_findings: Dict[str, Any],
        network_findings: Dict[str, Any]
    ) -> list:
        """Extract auto-detected suspicious indicators."""
        indicators = []
        
        if not page_load.get('ssl') and dom_findings.get('password_fields'):
            indicators.append("Password fields on non-HTTPS page")
        
        if js_findings.get('suspicious_patterns'):
            indicators.append(f"{len(js_findings['suspicious_patterns'])} suspicious JavaScript patterns")
        
        if network_findings.get('exfiltration_candidates'):
            indicators.append(f"{len(network_findings['exfiltration_candidates'])} potential data exfiltration endpoints")
        
        if dom_findings.get('hidden_inputs'):
            indicators.append(f"{len(dom_findings['hidden_inputs'])} hidden input fields")
        
        return indicators
    
    def _parse_judge_verdict(self, judge_ruling: str) -> Dict[str, Any]:
        """
        Parse judge's ruling to extract structured verdict.
        
        Expected format:
        📊 RISK SCORE: 75/100
        🏛️ FINAL VERDICT: PHISHING
        📝 REASONING: ...
        """
        verdict_data = {
            "verdict": "Unknown",
            "confidence": 50,
            "risk_score": 50,
            "reasoning": "",
            "full_ruling": judge_ruling,
        }
        
        # Extract risk score
        risk_match = re.search(r'RISK SCORE:\s*(\d+)/100', judge_ruling, re.IGNORECASE)
        if risk_match:
            verdict_data["risk_score"] = int(risk_match.group(1))
            verdict_data["confidence"] = int(risk_match.group(1))
        
        # Extract verdict
        verdict_match = re.search(r'FINAL VERDICT:\s*(\w+)', judge_ruling, re.IGNORECASE)
        if verdict_match:
            verdict_data["verdict"] = verdict_match.group(1).upper()
        
        # Extract reasoning
        reasoning_match = re.search(r'REASONING:\s*(.+?)(?:\n\n|\Z)', judge_ruling, re.IGNORECASE | re.DOTALL)
        if reasoning_match:
            verdict_data["reasoning"] = reasoning_match.group(1).strip()
        
        return verdict_data

# Made with Bob
