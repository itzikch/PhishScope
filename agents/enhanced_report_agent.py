"""
EnhancedReportAgent - Advanced reporting with PDF, IOC extraction, and MITRE ATT&CK mapping
"""

import logging
import json
import re
from pathlib import Path
from typing import Dict, Any, List, Set
from datetime import datetime
from urllib.parse import urlparse


class EnhancedReportAgent:
    """
    Enhanced reporting capabilities:
    - PDF report generation
    - IOC (Indicators of Compromise) extraction
    - MITRE ATT&CK technique mapping
    - Executive summary generation
    """
    
    # MITRE ATT&CK techniques relevant to phishing
    MITRE_TECHNIQUES = {
        "T1566": {
            "name": "Phishing",
            "description": "Adversaries may send phishing messages to gain access to victim systems",
            "tactics": ["Initial Access"]
        },
        "T1566.002": {
            "name": "Phishing: Spearphishing Link",
            "description": "Adversaries may send spearphishing emails with a malicious link",
            "tactics": ["Initial Access"]
        },
        "T1056.003": {
            "name": "Input Capture: Web Portal Capture",
            "description": "Adversaries may install code on externally facing portals to capture credentials",
            "tactics": ["Collection", "Credential Access"]
        },
        "T1185": {
            "name": "Browser Session Hijacking",
            "description": "Adversaries may take advantage of security vulnerabilities to hijack web sessions",
            "tactics": ["Collection"]
        },
        "T1539": {
            "name": "Steal Web Session Cookie",
            "description": "Adversaries may steal web application or service session cookies",
            "tactics": ["Credential Access"]
        },
        "T1114": {
            "name": "Email Collection",
            "description": "Adversaries may target user email to collect sensitive information",
            "tactics": ["Collection"]
        },
        "T1583.001": {
            "name": "Acquire Infrastructure: Domains",
            "description": "Adversaries may acquire domains for use during targeting",
            "tactics": ["Resource Development"]
        }
    }
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def extract_iocs(self, results: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Extract Indicators of Compromise from analysis results
        
        Returns:
            Dictionary with IOC types and their values
        """
        iocs = {
            "domains": set(),
            "urls": set(),
            "ip_addresses": set(),
            "email_addresses": set(),
            "file_hashes": set(),
            "suspicious_strings": set()
        }
        
        try:
            # Extract from URL
            url = results.get("url", "")
            if url:
                iocs["urls"].add(url)
                parsed = urlparse(url)
                if parsed.netloc:
                    iocs["domains"].add(parsed.netloc)
            
            # Extract from page load
            page_load = results.get("page_load", {})
            final_url = page_load.get("final_url")
            if final_url and final_url != url:
                iocs["urls"].add(final_url)
                parsed = urlparse(final_url)
                if parsed.netloc:
                    iocs["domains"].add(parsed.netloc)
            
            # Extract from network findings
            network = results.get("findings", {}).get("network", {})
            
            # Exfiltration endpoints
            for candidate in network.get("exfiltration_candidates", []):
                domain = candidate.get("domain")
                url = candidate.get("url")
                if domain:
                    iocs["domains"].add(domain)
                if url:
                    iocs["urls"].add(url)
            
            # Third-party domains
            for domain_info in network.get("third_party_domains", []):
                domain = domain_info.get("domain")
                if domain:
                    iocs["domains"].add(domain)
            
            # Suspicious endpoints
            for endpoint in network.get("suspicious_endpoints", []):
                domain = endpoint.get("domain")
                url = endpoint.get("url")
                if domain:
                    iocs["domains"].add(domain)
                if url:
                    iocs["urls"].add(url)
            
            # Extract IP addresses from domains
            for domain in list(iocs["domains"]):
                if self._is_ip_address(domain):
                    iocs["ip_addresses"].add(domain)
            
            # Extract from JavaScript findings
            js = results.get("findings", {}).get("javascript", {})
            for source in js.get("external_sources", []):
                parsed = urlparse(source)
                if parsed.netloc:
                    iocs["domains"].add(parsed.netloc)
                iocs["urls"].add(source)
            
            # Extract email addresses from DOM
            dom = results.get("findings", {}).get("dom", {})
            # Look for email patterns in forms and hidden inputs
            for form in dom.get("forms", []):
                action = form.get("action", "")
                emails = self._extract_emails(action)
                iocs["email_addresses"].update(emails)
            
            self.logger.info(f"Extracted IOCs: {len(iocs['domains'])} domains, {len(iocs['urls'])} URLs, {len(iocs['ip_addresses'])} IPs")
            
        except Exception as e:
            self.logger.error(f"IOC extraction failed: {str(e)}")
        
        # Convert sets to sorted lists
        return {k: sorted(list(v)) for k, v in iocs.items() if v}
    
    def map_mitre_techniques(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Map findings to MITRE ATT&CK techniques
        
        Returns:
            List of applicable MITRE techniques with evidence
        """
        techniques = []
        
        try:
            findings = results.get("findings", {})
            dom = findings.get("dom", {})
            js = findings.get("javascript", {})
            network = findings.get("network", {})
            
            # T1566 - Phishing (always applicable for phishing analysis)
            techniques.append({
                "id": "T1566",
                "name": self.MITRE_TECHNIQUES["T1566"]["name"],
                "description": self.MITRE_TECHNIQUES["T1566"]["description"],
                "tactics": self.MITRE_TECHNIQUES["T1566"]["tactics"],
                "evidence": ["Phishing page analysis context"],
                "confidence": "High"
            })
            
            # T1566.002 - Spearphishing Link
            if results.get("url"):
                techniques.append({
                    "id": "T1566.002",
                    "name": self.MITRE_TECHNIQUES["T1566.002"]["name"],
                    "description": self.MITRE_TECHNIQUES["T1566.002"]["description"],
                    "tactics": self.MITRE_TECHNIQUES["T1566.002"]["tactics"],
                    "evidence": [f"Malicious URL: {results.get('url')}"],
                    "confidence": "High"
                })
            
            # T1056.003 - Web Portal Capture
            if dom.get("forms_count", 0) > 0 and dom.get("password_fields"):
                evidence = [
                    f"Detected {dom['forms_count']} form(s) with password fields",
                    f"Forms designed to capture credentials"
                ]
                techniques.append({
                    "id": "T1056.003",
                    "name": self.MITRE_TECHNIQUES["T1056.003"]["name"],
                    "description": self.MITRE_TECHNIQUES["T1056.003"]["description"],
                    "tactics": self.MITRE_TECHNIQUES["T1056.003"]["tactics"],
                    "evidence": evidence,
                    "confidence": "High"
                })
            
            # T1185 - Browser Session Hijacking (if JavaScript manipulation detected)
            js_patterns = js.get("suspicious_patterns", [])
            if any(p.get("pattern") in ["input_listener", "keydown_listener"] for p in js_patterns):
                evidence = [
                    "JavaScript event listeners on input fields",
                    "Real-time credential capture capability"
                ]
                techniques.append({
                    "id": "T1185",
                    "name": self.MITRE_TECHNIQUES["T1185"]["name"],
                    "description": self.MITRE_TECHNIQUES["T1185"]["description"],
                    "tactics": self.MITRE_TECHNIQUES["T1185"]["tactics"],
                    "evidence": evidence,
                    "confidence": "Medium"
                })
            
            # T1539 - Steal Web Session Cookie
            if any(p.get("pattern") == "credential_keywords" for p in js_patterns):
                techniques.append({
                    "id": "T1539",
                    "name": self.MITRE_TECHNIQUES["T1539"]["name"],
                    "description": self.MITRE_TECHNIQUES["T1539"]["description"],
                    "tactics": self.MITRE_TECHNIQUES["T1539"]["tactics"],
                    "evidence": ["JavaScript accessing credential-related data"],
                    "confidence": "Medium"
                })
            
            # T1583.001 - Acquire Infrastructure: Domains
            if network.get("exfiltration_candidates"):
                domains = [c.get("domain") for c in network["exfiltration_candidates"]]
                evidence = [f"Suspicious domains used: {', '.join(domains[:3])}"]
                techniques.append({
                    "id": "T1583.001",
                    "name": self.MITRE_TECHNIQUES["T1583.001"]["name"],
                    "description": self.MITRE_TECHNIQUES["T1583.001"]["description"],
                    "tactics": self.MITRE_TECHNIQUES["T1583.001"]["tactics"],
                    "evidence": evidence,
                    "confidence": "High"
                })
            
            self.logger.info(f"Mapped {len(techniques)} MITRE ATT&CK techniques")
            
        except Exception as e:
            self.logger.error(f"MITRE mapping failed: {str(e)}")
        
        return techniques
    
    def generate_executive_summary(self, results: Dict[str, Any], iocs: Dict[str, List[str]], 
                                   mitre_techniques: List[Dict[str, Any]]) -> str:
        """Generate executive summary for leadership"""
        
        findings = results.get("findings", {})
        dom = findings.get("dom", {})
        js = findings.get("javascript", {})
        network = findings.get("network", {})
        
        # Determine threat level
        threat_score = 0
        if dom.get("forms_count", 0) > 0:
            threat_score += 25
        if len(dom.get("password_fields", [])) > 0:
            threat_score += 25
        if len(js.get("suspicious_patterns", [])) >= 3:
            threat_score += 25
        if len(network.get("exfiltration_candidates", [])) > 0:
            threat_score += 25
        
        if threat_score >= 75:
            threat_level = "CRITICAL"
            recommendation = "Immediate action required. Block URL and alert affected users."
        elif threat_score >= 50:
            threat_level = "HIGH"
            recommendation = "Urgent investigation required. Consider blocking URL."
        elif threat_score >= 25:
            threat_level = "MEDIUM"
            recommendation = "Further investigation recommended."
        else:
            threat_level = "LOW"
            recommendation = "Monitor for suspicious activity."
        
        summary = f"""
EXECUTIVE SUMMARY
=================

Threat Level: {threat_level}
Threat Score: {threat_score}/100

Target URL: {results.get('url', 'N/A')}
Analysis Date: {results.get('timestamp', 'N/A')}

KEY FINDINGS:
- {len(iocs.get('domains', []))} suspicious domain(s) identified
- {len(iocs.get('urls', []))} malicious URL(s) detected
- {len(mitre_techniques)} MITRE ATT&CK technique(s) observed
- {dom.get('forms_count', 0)} credential collection form(s) found

ATTACK METHODOLOGY:
{self._describe_attack_flow(findings)}

RECOMMENDATION:
{recommendation}

MITRE ATT&CK TECHNIQUES:
{self._format_mitre_summary(mitre_techniques)}
"""
        return summary
    
    def generate_pdf_report(self, results: Dict[str, Any], output_dir: Path) -> Path:
        """
        Generate PDF report (placeholder - requires reportlab or weasyprint)
        
        For now, generates an enhanced markdown that can be converted to PDF
        """
        try:
            # Get enhanced data
            iocs = self.extract_iocs(results)
            mitre_techniques = self.map_mitre_techniques(results)
            exec_summary = self.generate_executive_summary(results, iocs, mitre_techniques)
            
            # Generate enhanced markdown
            md_content = self._generate_enhanced_markdown(results, iocs, mitre_techniques, exec_summary)
            
            # Save enhanced markdown
            enhanced_md_path = output_dir / "report_enhanced.md"
            with open(enhanced_md_path, "w", encoding="utf-8") as f:
                f.write(md_content)
            
            # Save IOCs as JSON
            ioc_path = output_dir / "iocs.json"
            with open(ioc_path, "w", encoding="utf-8") as f:
                json.dump(iocs, f, indent=2)
            
            # Save MITRE mapping
            mitre_path = output_dir / "mitre_attack.json"
            with open(mitre_path, "w", encoding="utf-8") as f:
                json.dump(mitre_techniques, f, indent=2)
            
            self.logger.info(f"Enhanced reports generated: {enhanced_md_path}")
            
            return enhanced_md_path
            
        except Exception as e:
            self.logger.error(f"PDF report generation failed: {str(e)}")
            raise
    
    def _generate_enhanced_markdown(self, results: Dict[str, Any], iocs: Dict[str, List[str]],
                                    mitre_techniques: List[Dict[str, Any]], exec_summary: str) -> str:
        """Generate enhanced markdown report"""
        
        lines = []
        lines.append("# PhishScope Enhanced Investigation Report")
        lines.append("")
        lines.append(exec_summary)
        lines.append("")
        
        # IOCs Section
        lines.append("## Indicators of Compromise (IOCs)")
        lines.append("")
        for ioc_type, values in iocs.items():
            if values:
                lines.append(f"### {ioc_type.replace('_', ' ').title()}")
                for value in values:
                    lines.append(f"- `{value}`")
                lines.append("")
        
        # MITRE ATT&CK Section
        lines.append("## MITRE ATT&CK Techniques")
        lines.append("")
        for technique in mitre_techniques:
            lines.append(f"### {technique['id']}: {technique['name']}")
            lines.append(f"**Tactics:** {', '.join(technique['tactics'])}")
            lines.append(f"**Confidence:** {technique['confidence']}")
            lines.append("")
            lines.append(f"**Description:** {technique['description']}")
            lines.append("")
            lines.append("**Evidence:**")
            for evidence in technique['evidence']:
                lines.append(f"- {evidence}")
            lines.append("")
        
        # Detailed Findings (from original report)
        findings = results.get("findings", {})
        lines.append("## Detailed Technical Findings")
        lines.append("")
        
        # Add DOM, JS, Network sections...
        lines.append("### DOM Analysis")
        dom = findings.get("dom", {})
        lines.append(f"- Forms: {dom.get('forms_count', 0)}")
        lines.append(f"- Password Fields: {len(dom.get('password_fields', []))}")
        lines.append("")
        
        lines.append("### JavaScript Analysis")
        js = findings.get("javascript", {})
        lines.append(f"- Suspicious Patterns: {len(js.get('suspicious_patterns', []))}")
        lines.append("")
        
        lines.append("### Network Analysis")
        network = findings.get("network", {})
        lines.append(f"- Exfiltration Candidates: {len(network.get('exfiltration_candidates', []))}")
        lines.append("")
        
        lines.append("---")
        lines.append("*Generated by PhishScope Enhanced Reporting*")
        
        return "\n".join(lines)
    
    def _describe_attack_flow(self, findings: Dict[str, Any]) -> str:
        """Describe the attack flow based on findings"""
        steps = []
        
        dom = findings.get("dom", {})
        js = findings.get("javascript", {})
        network = findings.get("network", {})
        
        if dom.get("forms_count", 0) > 0:
            steps.append("1. Victim lands on fake login page")
            steps.append("2. Victim enters credentials into spoofed form")
        
        if js.get("suspicious_patterns"):
            steps.append("3. JavaScript intercepts credentials before submission")
        
        if network.get("exfiltration_candidates"):
            steps.append("4. Credentials exfiltrated to attacker-controlled server")
        
        if not steps:
            steps.append("Attack flow could not be determined from available evidence")
        
        return "\n".join(steps)
    
    def _format_mitre_summary(self, techniques: List[Dict[str, Any]]) -> str:
        """Format MITRE techniques for summary"""
        if not techniques:
            return "None identified"
        
        lines = []
        for tech in techniques[:5]:  # Top 5
            lines.append(f"- {tech['id']}: {tech['name']} ({tech['confidence']} confidence)")
        
        return "\n".join(lines)
    
    def _is_ip_address(self, domain: str) -> bool:
        """Check if string is an IP address"""
        domain = domain.split(':')[0]
        parts = domain.split('.')
        if len(parts) == 4:
            return all(part.isdigit() and 0 <= int(part) <= 255 for part in parts)
        return False
    
    def _extract_emails(self, text: str) -> Set[str]:
        """Extract email addresses from text"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return set(re.findall(email_pattern, text))


# Made with Bob