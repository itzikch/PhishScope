"""
LLM prompts for phishing analysis.
"""

from typing import Dict, Any, List


def build_assessment_prompt(
    dom_findings: Dict[str, Any],
    js_findings: Dict[str, Any],
    network_findings: Dict[str, Any]
) -> str:
    """
    Build a prompt for phishing risk assessment.

    Args:
        dom_findings: DOM analysis findings
        js_findings: JavaScript analysis findings
        network_findings: Network analysis findings

    Returns:
        Formatted prompt string
    """
    context = _prepare_findings_context(dom_findings, js_findings, network_findings)

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

    return prompt


def build_attack_analysis_prompt(
    dom_findings: Dict[str, Any],
    js_findings: Dict[str, Any],
    network_findings: Dict[str, Any]
) -> str:
    """
    Build a prompt for attack methodology analysis.

    Args:
        dom_findings: DOM analysis findings
        js_findings: JavaScript analysis findings
        network_findings: Network analysis findings

    Returns:
        Formatted prompt string
    """
    context = _prepare_findings_context(dom_findings, js_findings, network_findings)

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

    return prompt


def build_recommendations_prompt(
    verdict: str,
    dom_findings: Dict[str, Any],
    js_findings: Dict[str, Any],
    network_findings: Dict[str, Any]
) -> str:
    """
    Build a prompt for security recommendations.

    Args:
        verdict: Risk assessment verdict
        dom_findings: DOM analysis findings
        js_findings: JavaScript analysis findings
        network_findings: Network analysis findings

    Returns:
        Formatted prompt string
    """
    context = _prepare_findings_context(dom_findings, js_findings, network_findings)

    prompt = f"""You are a security consultant. The phishing risk assessment is: {verdict}

FINDINGS:
{context}

Provide 5-7 actionable security recommendations for:
1. Immediate response actions
2. Detection and monitoring
3. User education

Format as a bullet list."""

    return prompt


def _prepare_findings_context(
    dom_findings: Dict[str, Any],
    js_findings: Dict[str, Any],
    network_findings: Dict[str, Any]
) -> str:
    """
    Prepare findings as context for AI prompts.

    Args:
        dom_findings: DOM analysis findings
        js_findings: JavaScript analysis findings
        network_findings: Network analysis findings

    Returns:
        Formatted context string
    """
    context_parts = []

    # DOM findings
    if dom_findings.get('forms_count', 0) > 0:
        context_parts.append(f"- {dom_findings['forms_count']} login form(s) detected")
    if dom_findings.get('password_fields'):
        context_parts.append(f"- {len(dom_findings['password_fields'])} password field(s)")
    if dom_findings.get('hidden_inputs'):
        context_parts.append(f"- {len(dom_findings['hidden_inputs'])} hidden input(s)")
    if dom_findings.get('suspicious_iframes'):
        context_parts.append(
            f"- {len(dom_findings['suspicious_iframes'])} suspicious iframe(s)"
        )

    # JavaScript findings
    if js_findings.get('suspicious_patterns'):
        patterns = js_findings['suspicious_patterns']
        context_parts.append(f"- {len(patterns)} suspicious JavaScript pattern(s)")
        for pattern in patterns[:3]:
            context_parts.append(
                f"  * {pattern.get('pattern', 'unknown')}: {pattern.get('description', '')}"
            )

    # Network findings
    if network_findings.get('exfiltration_candidates'):
        candidates = network_findings['exfiltration_candidates']
        context_parts.append(
            f"- {len(candidates)} potential data exfiltration endpoint(s)"
        )
        for candidate in candidates[:3]:
            context_parts.append(f"  * {candidate.get('domain', 'unknown')}")

    if network_findings.get('suspicious_endpoints'):
        endpoints = network_findings['suspicious_endpoints']
        context_parts.append(f"- {len(endpoints)} suspicious API endpoint(s)")

    return '\n'.join(context_parts) if context_parts else "No significant findings detected"
