"""
Workflow Node Implementations

This module contains the node functions for the phishing analysis workflow.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from langgraph.graph import END
from langgraph.types import Command

from phishscope.workflow.state import WorkflowState, WorkflowStatus
from phishscope.workflow.node_types import (
    DOM_ANALYSIS_NODE,
    JS_ANALYSIS_NODE,
    NETWORK_ANALYSIS_NODE,
    AI_ANALYSIS_NODE,
    REPORT_GENERATION_NODE,
    CLEANUP_NODE,
)


logger = logging.getLogger(__name__)

# Module-level state for page context (not serializable, must be managed separately)
_page_contexts = {}


async def page_load_node(state: WorkflowState) -> Command:
    """
    Node that loads the target URL and captures initial page state.

    CRITICAL: The Playwright Page object is NOT JSON-serializable.
    We store it in module-level state and pass only serializable data.
    """
    from phishscope.core.page_loader import PageLoader

    url = state.get("url")
    output_dir = Path(state.get("output_dir", "./reports"))
    workflow_id = state.get("workflow_id")

    if not url:
        return Command(
            goto=CLEANUP_NODE,
            update={
                "status": WorkflowStatus.FAILED.value,
                "error": "No URL provided",
            },
        )

    try:
        logger.info(f"Loading page: {url}")
        output_dir.mkdir(parents=True, exist_ok=True)

        page_loader = PageLoader()
        page_data = await page_loader.load_page(url, output_dir)

        # CRITICAL: Extract page_context before storing in state
        # The Playwright Page object is NOT JSON-serializable
        page_context = page_data.pop("page_context", None)

        # Store page context and loader in module-level state for later cleanup
        _page_contexts[workflow_id] = {
            "page_context": page_context,
            "page_loader": page_loader,
        }

        if not page_data.get("success"):
            return Command(
                goto=CLEANUP_NODE,
                update={
                    "page_load_result": page_data,
                    "status": WorkflowStatus.FAILED.value,
                    "error": page_data.get("error", "Page load failed"),
                },
            )

        return Command(
            goto=DOM_ANALYSIS_NODE,
            update={
                "page_load_result": page_data,
                "network_log": page_data.get("network_log", []),
            },
        )

    except Exception as exc:
        logger.exception("Page load failed")
        return Command(
            goto=CLEANUP_NODE,
            update={
                "status": WorkflowStatus.FAILED.value,
                "error": str(exc),
            },
        )


async def dom_analysis_node(state: WorkflowState) -> Command:
    """Node that performs DOM analysis."""
    from phishscope.core.analyzers.dom import DOMAnalyzer

    workflow_id = state.get("workflow_id")
    output_dir = Path(state.get("output_dir", "./reports"))

    try:
        logger.info("Analyzing DOM...")

        # Get page context from module-level state
        page_context = None
        if workflow_id in _page_contexts:
            page_context = _page_contexts[workflow_id].get("page_context")

        analyzer = DOMAnalyzer()
        findings = await analyzer.analyze(page=page_context, output_dir=output_dir)

        return Command(
            goto=JS_ANALYSIS_NODE,
            update={"dom_findings": findings},
        )

    except Exception as exc:
        logger.exception("DOM analysis failed")
        return Command(
            goto=CLEANUP_NODE,
            update={
                "status": WorkflowStatus.FAILED.value,
                "error": str(exc),
            },
        )


async def js_analysis_node(state: WorkflowState) -> Command:
    """Node that performs JavaScript analysis."""
    from phishscope.core.analyzers.javascript import JavaScriptAnalyzer

    workflow_id = state.get("workflow_id")
    output_dir = Path(state.get("output_dir", "./reports"))

    try:
        logger.info("Analyzing JavaScript...")

        # Get page context from module-level state
        page_context = None
        if workflow_id in _page_contexts:
            page_context = _page_contexts[workflow_id].get("page_context")

        analyzer = JavaScriptAnalyzer()
        findings = await analyzer.analyze(page=page_context, output_dir=output_dir)

        return Command(
            goto=NETWORK_ANALYSIS_NODE,
            update={"js_findings": findings},
        )

    except Exception as exc:
        logger.exception("JavaScript analysis failed")
        return Command(
            goto=CLEANUP_NODE,
            update={
                "status": WorkflowStatus.FAILED.value,
                "error": str(exc),
            },
        )


async def network_analysis_node(state: WorkflowState) -> Command:
    """Node that performs network traffic analysis."""
    from phishscope.core.analyzers.network import NetworkAnalyzer

    output_dir = Path(state.get("output_dir", "./reports"))
    network_log = state.get("network_log", [])

    try:
        logger.info("Analyzing network traffic...")

        analyzer = NetworkAnalyzer()
        findings = await analyzer.analyze(network_log=network_log, output_dir=output_dir)

        return Command(
            goto=AI_ANALYSIS_NODE,
            update={"network_findings": findings},
        )

    except Exception as exc:
        logger.exception("Network analysis failed")
        return Command(
            goto=CLEANUP_NODE,
            update={
                "status": WorkflowStatus.FAILED.value,
                "error": str(exc),
            },
        )


async def ai_analysis_node(state: WorkflowState) -> Command:
    """Node that performs LLM-based analysis."""
    from phishscope.llm.clients import get_chat_llm_client, is_llm_available
    from phishscope.llm.prompts import build_assessment_prompt

    dom_findings = state.get("dom_findings", {})
    js_findings = state.get("js_findings", {})
    network_findings = state.get("network_findings", {})

    try:
        if not is_llm_available():
            logger.info("LLM not available, using fallback assessment")
            findings = _fallback_assessment(dom_findings, js_findings, network_findings)
            return Command(
                goto=REPORT_GENERATION_NODE,
                update={"ai_findings": findings},
            )

        logger.info("Running AI analysis...")
        llm_client = get_chat_llm_client()

        # Build and execute prompt
        prompt = build_assessment_prompt(dom_findings, js_findings, network_findings)
        response = await llm_client.ainvoke(prompt)
        content = response.content if hasattr(response, 'content') else str(response)

        # Parse response
        findings = _parse_llm_response(content)

        return Command(
            goto=REPORT_GENERATION_NODE,
            update={"ai_findings": findings},
        )

    except Exception as exc:
        logger.warning(f"AI analysis failed, using fallback: {exc}")
        findings = _fallback_assessment(dom_findings, js_findings, network_findings)
        return Command(
            goto=REPORT_GENERATION_NODE,
            update={"ai_findings": findings},
        )


async def report_generation_node(state: WorkflowState) -> Command:
    """Node that generates the analysis report."""
    from phishscope.core.report_generator import ReportGenerator

    output_dir = Path(state.get("output_dir", "./reports"))

    try:
        logger.info("Generating report...")

        # Build results structure
        results = {
            "url": state.get("url"),
            "timestamp": state.get("start_time"),
            "page_load": state.get("page_load_result", {}),
            "findings": {
                "dom": state.get("dom_findings", {}),
                "javascript": state.get("js_findings", {}),
                "network": state.get("network_findings", {}),
                "ai_analysis": state.get("ai_findings", {}),
            }
        }

        generator = ReportGenerator()
        report_path = await generator.generate_report(results, output_dir)

        return Command(
            goto=CLEANUP_NODE,
            update={
                "report_path": str(report_path),
                "status": WorkflowStatus.COMPLETED.value,
            },
        )

    except Exception as exc:
        logger.exception("Report generation failed")
        return Command(
            goto=CLEANUP_NODE,
            update={
                "status": WorkflowStatus.FAILED.value,
                "error": str(exc),
            },
        )


async def cleanup_node(state: WorkflowState) -> Command:
    """
    Node that performs cleanup operations.

    MUST always run (both success and failure paths) to clean up browser resources.
    """
    workflow_id = state.get("workflow_id")

    try:
        # Cleanup page loader
        if workflow_id in _page_contexts:
            context_data = _page_contexts.pop(workflow_id)
            page_loader = context_data.get("page_loader")
            if page_loader:
                await page_loader.cleanup()
                logger.debug("Browser cleanup complete")

    except Exception as exc:
        logger.warning(f"Cleanup error: {exc}")

    # Preserve FAILED status if already set, otherwise mark as COMPLETED
    current_status = state.get("status")
    final_status = (
        current_status
        if current_status == WorkflowStatus.FAILED.value
        else WorkflowStatus.COMPLETED.value
    )

    return Command(
        goto=END,
        update={
            "status": final_status,
            "end_time": datetime.now().isoformat(),
        },
    )


def _parse_llm_response(response: str) -> dict:
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
            keywords = ['VERDICT:', 'CONFIDENCE:', 'KEY INDICATORS:', 'ATTACK TYPE:']
            if not any(x in line for x in keywords):
                result["phishing_assessment"]["reasoning"] += ' ' + line

    return result


def _fallback_assessment(
    dom_findings: dict,
    js_findings: dict,
    network_findings: dict
) -> dict:
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
