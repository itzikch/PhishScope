"""
PhishingAnalyzer - Coordinator class that orchestrates the analysis pipeline.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from phishscope.core.page_loader import PageLoader
from phishscope.core.analyzers.dom import DOMAnalyzer
from phishscope.core.analyzers.javascript import JavaScriptAnalyzer
from phishscope.core.analyzers.network import NetworkAnalyzer
from phishscope.core.report_generator import ReportGenerator


logger = logging.getLogger(__name__)


class PhishingAnalyzer:
    """
    Main coordinator for phishing analysis.

    Orchestrates the analysis pipeline:
    1. Load page with PageLoader
    2. Run DOM analysis
    3. Run JavaScript analysis
    4. Run Network analysis
    5. (Optional) Run LLM analysis
    6. Generate reports
    """

    def __init__(self, use_llm: bool = True):
        """
        Initialize the phishing analyzer.

        Args:
            use_llm: Whether to use LLM for enhanced analysis
        """
        self.use_llm = use_llm
        self.page_loader = PageLoader()
        self.dom_analyzer = DOMAnalyzer()
        self.js_analyzer = JavaScriptAnalyzer()
        self.network_analyzer = NetworkAnalyzer()
        self.report_generator = ReportGenerator()
        self.llm_client = None

        if use_llm:
            try:
                from phishscope.llm.clients import get_chat_llm_client, is_llm_available
                if is_llm_available():
                    self.llm_client = get_chat_llm_client()
                    logger.info("LLM client initialized")
                else:
                    logger.warning("LLM not available - using rule-based analysis only")
            except Exception as e:
                logger.warning(f"Failed to initialize LLM client: {e}")

    async def analyze(self, url: str, output_dir: Path) -> Dict[str, Any]:
        """
        Run complete phishing analysis pipeline.

        Args:
            url: Target URL to analyze
            output_dir: Directory to save artifacts and reports

        Returns:
            Dictionary containing all analysis results
        """
        logger.info(f"Starting analysis of: {url}")

        results = {
            "url": url,
            "timestamp": datetime.utcnow().isoformat(),
            "findings": {}
        }

        page_context = None

        try:
            # Ensure output directory exists
            output_dir.mkdir(parents=True, exist_ok=True)

            # Step 1: Load page and capture screenshot
            logger.info("[1/6] Loading page...")
            page_data = await self.page_loader.load_page(url, output_dir)

            # CRITICAL: Extract page context (Playwright Page object) before storing
            # The page_context is NOT JSON-serializable and must be popped
            page_context = page_data.pop("page_context", None)
            results["page_load"] = page_data

            if not page_data.get("success"):
                logger.error("Failed to load page. Aborting analysis.")
                results["error"] = "Page load failed"
                return results

            # Step 2: DOM Analysis
            logger.info("[2/6] Analyzing DOM...")
            dom_findings = await self.dom_analyzer.analyze(
                page=page_context,
                output_dir=output_dir
            )
            results["findings"]["dom"] = dom_findings

            # Step 3: JavaScript Analysis
            logger.info("[3/6] Analyzing JavaScript...")
            js_findings = await self.js_analyzer.analyze(
                page=page_context,
                output_dir=output_dir
            )
            results["findings"]["javascript"] = js_findings

            # Step 4: Network Analysis
            logger.info("[4/6] Analyzing network traffic...")
            network_findings = await self.network_analyzer.analyze(
                network_log=page_data.get("network_log", []),
                output_dir=output_dir
            )
            results["findings"]["network"] = network_findings

            # Step 5: LLM Analysis (optional)
            if self.llm_client:
                logger.info("[5/6] Running LLM analysis...")
                ai_findings = await self._run_llm_analysis(
                    dom_findings, js_findings, network_findings
                )
                results["findings"]["ai_analysis"] = ai_findings
            else:
                logger.info("[5/6] Skipping LLM analysis (not configured)")
                results["findings"]["ai_analysis"] = self._fallback_assessment(
                    dom_findings, js_findings, network_findings
                )

            # Step 6: Generate Report
            logger.info("[6/6] Generating report...")
            report_path = await self.report_generator.generate_report(
                results, output_dir
            )
            results["report_path"] = str(report_path)

            logger.info(f"Analysis complete. Report saved to: {report_path}")

        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}", exc_info=True)
            results["error"] = str(e)

        finally:
            # CRITICAL: Always cleanup browser resources
            await self.page_loader.cleanup()

        return results

    async def _run_llm_analysis(
        self,
        dom_findings: Dict[str, Any],
        js_findings: Dict[str, Any],
        network_findings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run LLM-powered analysis on findings."""
        try:
            from phishscope.llm.prompts import build_assessment_prompt

            # Build prompt with findings context
            prompt = build_assessment_prompt(dom_findings, js_findings, network_findings)

            # Invoke LLM
            response = await self.llm_client.ainvoke(prompt)
            content = response.content if hasattr(response, 'content') else str(response)

            # Parse response
            return self._parse_llm_response(content)

        except Exception as e:
            logger.error(f"LLM analysis failed: {e}")
            return self._fallback_assessment(dom_findings, js_findings, network_findings)

    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response into structured format."""
        result = {
            "ai_enabled": True,
            "phishing_assessment": {
                "verdict": "Unknown",
                "confidence": 50,
                "key_indicators": [],
                "reasoning": "",
                "attack_type": "",
                "full_response": response
            }
        }

        lines = response.split('\n')
        current_section = None

        for line in lines:
            line = line.strip()

            if 'VERDICT:' in line:
                result["phishing_assessment"]["verdict"] = (
                    line.split('VERDICT:')[-1].replace('**', '').strip()
                )
            elif 'CONFIDENCE:' in line:
                conf_str = line.split('CONFIDENCE:')[-1].replace('**', '').strip().rstrip('%')
                try:
                    result["phishing_assessment"]["confidence"] = int(conf_str)
                except ValueError:
                    pass
            elif 'KEY INDICATORS:' in line:
                current_section = 'indicators'
            elif 'REASONING:' in line:
                current_section = 'reasoning'
                result["phishing_assessment"]["reasoning"] = (
                    line.split('REASONING:')[-1].replace('**', '').strip()
                )
            elif 'ATTACK TYPE:' in line:
                result["phishing_assessment"]["attack_type"] = (
                    line.split('ATTACK TYPE:')[-1].replace('**', '').strip()
                )
            elif current_section == 'indicators' and line.startswith('-'):
                result["phishing_assessment"]["key_indicators"].append(line.lstrip('- '))
            elif current_section == 'reasoning' and line:
                if not any(x in line for x in ['VERDICT:', 'CONFIDENCE:', 'KEY INDICATORS:', 'ATTACK TYPE:']):
                    result["phishing_assessment"]["reasoning"] += ' ' + line

        return result

    def _fallback_assessment(
        self,
        dom_findings: Dict[str, Any],
        js_findings: Dict[str, Any],
        network_findings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Fallback rule-based assessment when LLM is unavailable."""
        risk_score = 0
        indicators = []

        # DOM-based scoring
        if dom_findings.get("forms_count", 0) > 0:
            risk_score += 30
            indicators.append("Login form detected")

        if dom_findings.get("password_fields"):
            risk_score += 25
            indicators.append("Password fields present")

        # JavaScript-based scoring
        if js_findings.get("suspicious_patterns"):
            pattern_count = len(js_findings["suspicious_patterns"])
            risk_score += min(pattern_count * 10, 30)
            indicators.append(f"{pattern_count} suspicious JS patterns")

        # Network-based scoring
        if network_findings.get("exfiltration_candidates"):
            risk_score += 25
            indicators.append("Potential data exfiltration endpoints")

        if network_findings.get("suspicious_endpoints"):
            risk_score += 15
            indicators.append("Suspicious API endpoints detected")

        # Determine verdict
        if risk_score >= 60:
            verdict = "High Risk"
        elif risk_score >= 30:
            verdict = "Medium Risk"
        else:
            verdict = "Low Risk"

        return {
            "ai_enabled": False,
            "phishing_assessment": {
                "verdict": verdict,
                "confidence": min(risk_score, 95),
                "key_indicators": indicators if indicators else ["No significant indicators"],
                "reasoning": f"Rule-based assessment (AI unavailable). Risk score: {risk_score}/100",
                "attack_type": "Credential phishing" if risk_score >= 50 else "Unknown"
            }
        }
