#!/usr/bin/env python3
"""
PhishScope - Evidence-Driven Phishing Analysis Agent
Main CLI entry point
"""

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, will use system environment variables

import argparse
import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from agents.page_loader import PageLoaderAgent
from agents.dom_inspector import DOMInspectorAgent
from agents.js_inspector import JavaScriptInspectorAgent
from agents.network_inspector import NetworkInspectorAgent
from agents.report_agent import ReportAgent
from agents.llm_agent import LLMAgent
from utils.logger import setup_logger


class PhishScope:
    """Main orchestrator for phishing analysis"""
    
    def __init__(self, url: str, output_dir: Path, verbose: bool = False, use_ai: bool = True):
        self.url = url
        self.output_dir = output_dir
        self.verbose = verbose
        self.use_ai = use_ai
        self.logger = setup_logger(verbose)
        
        # Initialize agents
        self.page_loader = PageLoaderAgent(self.logger)
        self.dom_inspector = DOMInspectorAgent(self.logger)
        self.js_inspector = JavaScriptInspectorAgent(self.logger)
        self.network_inspector = NetworkInspectorAgent(self.logger)
        self.report_agent = ReportAgent(self.logger)
        
        # Initialize AI agent (optional)
        self.llm_agent = None
        if use_ai:
            self.llm_agent = LLMAgent(self.logger)
            if self.llm_agent.is_available():
                provider = self.llm_agent.provider.upper()
                self.logger.info(f"✓ AI-enhanced analysis enabled ({provider})")
            else:
                self.logger.warning("⚠ AI not available - using rule-based analysis only")
        
    async def analyze(self) -> Dict[str, Any]:
        """
        Run complete phishing analysis pipeline
        
        Returns:
            Dictionary containing all analysis results
        """
        self.logger.info(f"Starting analysis of: {self.url}")
        
        results = {
            "url": self.url,
            "timestamp": datetime.utcnow().isoformat(),
            "findings": {}
        }
        
        try:
            # Step 1: Load page and capture screenshot
            self.logger.info("[1/5] Loading page...")
            page_data = await self.page_loader.load_page(self.url, self.output_dir)
            
            # Extract page context (Playwright Page object) before storing results
            page_context = page_data.pop("page_context", None)
            results["page_load"] = page_data
            
            if not page_data.get("success"):
                self.logger.error("Failed to load page. Aborting analysis.")
                results["error"] = "Page load failed"
                return results
            
            # Step 2: Inspect DOM
            self.logger.info("[2/5] Inspecting DOM...")
            dom_findings = await self.dom_inspector.inspect(
                page_context,
                self.output_dir
            )
            results["findings"]["dom"] = dom_findings
            
            # Step 3: Analyze JavaScript
            self.logger.info("[3/5] Analyzing JavaScript...")
            js_findings = await self.js_inspector.analyze(
                page_context,
                self.output_dir
            )
            results["findings"]["javascript"] = js_findings
            
            # Step 4: Analyze network traffic
            self.logger.info("[4/5] Analyzing network traffic...")
            network_findings = await self.network_inspector.analyze(
                page_data.get("network_log", []),
                self.output_dir
            )
            results["findings"]["network"] = network_findings
            
            # Step 5: AI-enhanced analysis (optional)
            if self.llm_agent and self.llm_agent.is_available():
                self.logger.info("[5/6] Running AI analysis...")
                ai_findings = self.llm_agent.analyze(
                    {
                        'dom': dom_findings,
                        'javascript': js_findings,
                        'network': network_findings
                    }
                )
                results["findings"]["ai_analysis"] = ai_findings
            else:
                self.logger.info("[5/6] Skipping AI analysis (not configured)")
            
            # Step 6: Generate report
            self.logger.info("[6/6] Generating report...")
            report_path = await self.report_agent.generate_report(
                results,
                self.output_dir
            )
            results["report_path"] = str(report_path)
            
            self.logger.info(f"Analysis complete. Report saved to: {report_path}")
            
        except Exception as e:
            self.logger.error(f"Analysis failed: {str(e)}", exc_info=True)
            results["error"] = str(e)
        
        finally:
            # Cleanup
            await self.page_loader.cleanup()
        
        return results


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description="PhishScope - Evidence-Driven Phishing Analysis Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  phishscope analyze https://suspicious-site.example.com
  phishscope analyze https://phishing.test --output ./reports/case001
  phishscope analyze https://phishing.test --verbose

Security Warning:
  PhishScope loads potentially malicious content. Always run in an isolated
  environment (VM or container) with proper network controls.
        """
    )
    
    parser.add_argument(
        "command",
        choices=["analyze"],
        help="Command to execute"
    )
    
    parser.add_argument(
        "url",
        help="URL to analyze"
    )
    
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=None,
        help="Output directory for reports (default: ./reports/case_TIMESTAMP)"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Page load timeout in seconds (default: 30)"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="PhishScope 0.1.0"
    )
    
    args = parser.parse_args()
    
    # Generate output directory if not specified
    if args.output is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        args.output = Path(f"./reports/case_{timestamp}")
    
    # Create output directory
    args.output.mkdir(parents=True, exist_ok=True)
    
    # Run analysis
    if args.command == "analyze":
        phishscope = PhishScope(args.url, args.output, args.verbose)
        results = asyncio.run(phishscope.analyze())
        
        # Save raw results
        results_file = args.output / "results.json"
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2)
        
        # Print summary
        if results.get("error"):
            print(f"\n❌ Analysis failed: {results['error']}")
            sys.exit(1)
        else:
            print(f"\n✅ Analysis complete!")
            print(f"📁 Report location: {args.output}")
            print(f"📄 View report: {results.get('report_path', 'N/A')}")
            
            # Print key findings summary
            findings = results.get("findings", {})
            dom = findings.get("dom", {})
            js = findings.get("javascript", {})
            network = findings.get("network", {})
            
            print("\n📊 Quick Summary:")
            print(f"  • Forms detected: {dom.get('forms_count', 0)}")
            print(f"  • Suspicious JS patterns: {len(js.get('suspicious_patterns', []))}")
            print(f"  • Exfiltration endpoints: {len(network.get('exfiltration_candidates', []))}")


if __name__ == "__main__":
    main()

# Made with Bob
