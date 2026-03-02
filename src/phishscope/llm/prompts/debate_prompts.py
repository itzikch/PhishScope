"""
Debate prompts for multi-agent phishing analysis.

This module contains prompts for the adversarial debate system:
- Prosecutor: Argues the site IS phishing
- Defense Attorney: Argues the site IS legitimate
- Judge: Makes final ruling after hearing both sides
"""

from typing import Dict, Any


def build_intelligence_report(
    url: str,
    page_load: Dict[str, Any],
    dom_findings: Dict[str, Any],
    js_findings: Dict[str, Any],
    network_findings: Dict[str, Any]
) -> str:
    """
    Build a structured intelligence report from analysis findings.
    
    Args:
        url: Target URL
        page_load: Page loading results
        dom_findings: DOM analysis results
        js_findings: JavaScript analysis results
        network_findings: Network analysis results
        
    Returns:
        Formatted intelligence report as string
    """
    report_sections = []
    
    # URL Analysis
    report_sections.append("=== URL ANALYSIS ===")
    report_sections.append(f"Target URL: {url}")
    report_sections.append(f"Final URL: {page_load.get('final_url', 'N/A')}")
    report_sections.append(f"SSL/HTTPS: {page_load.get('ssl', False)}")
    
    # Page Metadata
    report_sections.append("\n=== PAGE METADATA ===")
    report_sections.append(f"Title: {page_load.get('title', 'N/A')}")
    report_sections.append(f"Meta Description: {page_load.get('meta_description', 'N/A')}")
    
    # Redirect Chain
    redirects = page_load.get('redirect_chain', [])
    if redirects:
        report_sections.append("\n=== REDIRECT CHAIN ===")
        for i, redirect in enumerate(redirects, 1):
            report_sections.append(f"{i}. {redirect}")
    
    # Suspicious Indicators
    report_sections.append("\n=== SUSPICIOUS INDICATORS ===")
    suspicious = []
    
    # Check for password fields without SSL
    if not page_load.get('ssl') and dom_findings.get('password_fields'):
        suspicious.append("⚠️ Password fields on non-HTTPS page")
    
    # Check for suspicious patterns
    if js_findings.get('suspicious_patterns'):
        suspicious.append(f"⚠️ {len(js_findings['suspicious_patterns'])} suspicious JavaScript patterns detected")
    
    # Check for exfiltration candidates
    if network_findings.get('exfiltration_candidates'):
        suspicious.append(f"⚠️ {len(network_findings['exfiltration_candidates'])} potential data exfiltration endpoints")
    
    # Check for hidden inputs
    if dom_findings.get('hidden_inputs'):
        suspicious.append(f"⚠️ {len(dom_findings['hidden_inputs'])} hidden input fields")
    
    if suspicious:
        for indicator in suspicious:
            report_sections.append(indicator)
    else:
        report_sections.append("No automatic red flags detected")
    
    # Forms
    report_sections.append("\n=== FORMS ===")
    forms_count = dom_findings.get('forms_count', 0)
    report_sections.append(f"Total forms: {forms_count}")
    if forms_count > 0:
        report_sections.append(f"Password fields: {len(dom_findings.get('password_fields', []))}")
        report_sections.append(f"Hidden inputs: {len(dom_findings.get('hidden_inputs', []))}")
    
    # Input Fields
    report_sections.append("\n=== INPUT FIELDS ===")
    password_fields = dom_findings.get('password_fields', [])
    if password_fields:
        report_sections.append("Password fields detected:")
        for field in password_fields[:5]:  # Limit to first 5
            report_sections.append(f"  - {field}")
    
    # Scripts
    report_sections.append("\n=== SCRIPTS LOADED ===")
    report_sections.append(f"Inline scripts: {js_findings.get('inline_scripts_count', 0)}")
    report_sections.append(f"External scripts: {js_findings.get('external_scripts_count', 0)}")
    
    external_scripts = js_findings.get('external_scripts', [])
    if external_scripts:
        report_sections.append("External script sources:")
        for script in external_scripts[:10]:  # Limit to first 10
            report_sections.append(f"  - {script}")
    
    # Network Traffic
    report_sections.append("\n=== NETWORK TRAFFIC ===")
    report_sections.append(f"Total requests: {network_findings.get('total_requests', 0)}")
    report_sections.append(f"POST requests: {len(network_findings.get('post_requests', []))}")
    
    post_requests = network_findings.get('post_requests', [])
    if post_requests:
        report_sections.append("POST endpoints:")
        for req in post_requests[:5]:  # Limit to first 5
            report_sections.append(f"  - {req.get('url', 'N/A')}")
    
    # Page Errors
    page_errors = page_load.get('page_errors', [])
    if page_errors:
        report_sections.append("\n=== PAGE ERRORS ===")
        for error in page_errors[:5]:  # Limit to first 5
            report_sections.append(f"  - {error}")
    
    return "\n".join(report_sections)


def get_prosecutor_round1_prompt(intelligence_report: str) -> str:
    """Get prosecutor's opening argument prompt."""
    return f"""You are the PROSECUTOR in a phishing detection debate.
Your SOLE job is to find evidence this website IS a phishing attempt.

Analyze the provided intelligence report. Look for:
- Suspicious domain names (typosquatting, unusual TLDs, excessive hyphens)
- SSL/HTTPS issues or missing security
- Urgency or fear-inducing language
- Requests for sensitive information (passwords, credit cards)
- Brand impersonation attempts
- Poor grammar or unprofessional content
- Suspicious redirects or redirect chains
- Forms submitting to external/suspicious domains
- Multiple third-party scripts from unknown sources
- Hidden input fields
- JavaScript obfuscation or suspicious patterns
- Data exfiltration endpoints

Be aggressive and thorough. Cite SPECIFIC evidence from the report.
Focus on the STRONGEST indicators of phishing.

INTELLIGENCE REPORT:
{intelligence_report}

Format your response as:
🔴 PROSECUTION — Round 1:

[Your arguments in bullet points, each citing specific evidence]"""


def get_defense_round1_prompt(intelligence_report: str, prosecutor_args: str) -> str:
    """Get defense attorney's opening argument prompt."""
    return f"""You are the DEFENSE ATTORNEY in a phishing detection debate.
Your SOLE job is to find evidence this website IS legitimate.

You have heard the Prosecutor's arguments. Now analyze the intelligence report to defend the site.

Look for:
- Proper domain structure and reputable TLD (.com, .org, .edu, etc.)
- Valid SSL/HTTPS certificate
- Professional language and design
- Logical business purpose
- Consistent branding
- Reasonable forms (login, contact, newsletter)
- Standard security headers
- Legitimate third-party services (Google Analytics, CDNs)
- Normal website functionality

Be thorough and fair. Cite SPECIFIC evidence from the report.
Address the Prosecutor's concerns where you can refute them.

INTELLIGENCE REPORT:
{intelligence_report}

PROSECUTOR'S ARGUMENTS:
{prosecutor_args}

Format your response as:
🟢 DEFENSE — Round 1:

[Your arguments in bullet points, each citing specific evidence]"""


def get_prosecutor_round2_prompt(
    intelligence_report: str,
    prosecutor_r1: str,
    defense_r1: str
) -> str:
    """Get prosecutor's rebuttal prompt."""
    return f"""You are the PROSECUTOR in Round 2 (Rebuttal).

You heard the Defense's arguments. Now REBUT them and STRENGTHEN your case.

- Point out flaws in the Defense's reasoning
- Cite overlooked red flags from the intelligence report
- Explain why seemingly legitimate features could still be phishing
- Emphasize the most damning evidence

Be forceful but factual. Focus on evidence the Defense couldn't explain away.

INTELLIGENCE REPORT:
{intelligence_report}

YOUR ROUND 1 ARGUMENTS:
{prosecutor_r1}

DEFENSE'S ROUND 1 ARGUMENTS:
{defense_r1}

Format your response as:
🔴 PROSECUTION — Round 2 (Rebuttal):

[Your rebuttals in bullet points]"""


def get_defense_round2_prompt(
    intelligence_report: str,
    prosecutor_r1: str,
    defense_r1: str,
    prosecutor_r2: str
) -> str:
    """Get defense attorney's rebuttal prompt."""
    return f"""You are the DEFENSE ATTORNEY in Round 2 (Rebuttal).

You heard both Prosecutor rounds. Now REBUT and STRENGTHEN your defense.

- Explain why the Prosecutor's concerns are overblown or misinterpreted
- Provide alternative explanations for suspicious indicators
- Emphasize legitimate features the Prosecutor ignored
- Show how the evidence supports a legitimate site

Be thorough and persuasive. Address the Prosecutor's strongest points.

INTELLIGENCE REPORT:
{intelligence_report}

PROSECUTOR'S ROUND 1:
{prosecutor_r1}

YOUR ROUND 1 ARGUMENTS:
{defense_r1}

PROSECUTOR'S ROUND 2:
{prosecutor_r2}

Format your response as:
🟢 DEFENSE — Round 2 (Rebuttal):

[Your rebuttals in bullet points]"""


def get_judge_prompt(
    intelligence_report: str,
    prosecutor_r1: str,
    defense_r1: str,
    prosecutor_r2: str,
    defense_r2: str
) -> str:
    """Get judge's final ruling prompt."""
    return f"""You are the JUDGE in a phishing detection debate.

You reviewed all evidence and arguments from both sides.
Make a FINAL ruling based on the preponderance of evidence.

Consider:
- Which side presented stronger evidence?
- Are there clear phishing indicators that can't be explained away?
- Are there legitimate features that outweigh suspicious ones?
- What is the overall risk to users?

Format your response EXACTLY as follows:

⚖️ JUDGE'S RULING:

[Your analysis of both sides' arguments - 2-3 paragraphs]

📊 RISK SCORE: [NUMBER]/100
(0=definitely legitimate, 100=definitely phishing)

🏛️ FINAL VERDICT: [PHISHING/LEGITIMATE/SUSPICIOUS]

📝 REASONING:
[2-3 sentence summary of your decision]

INTELLIGENCE REPORT:
{intelligence_report}

FULL DEBATE TRANSCRIPT:

{prosecutor_r1}

{defense_r1}

{prosecutor_r2}

{defense_r2}

Now render your judgment."""

# Made with Bob
