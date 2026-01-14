#!/usr/bin/env python3
"""
PhishScope Enhanced CLI with Rich formatting
Beautiful terminal interface for phishing analysis
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

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich import box
from rich.tree import Tree

from agents.page_loader import PageLoaderAgent
from agents.dom_inspector import DOMInspectorAgent
from agents.js_inspector import JavaScriptInspectorAgent
from agents.network_inspector import NetworkInspectorAgent
from agents.report_agent import ReportAgent
from agents.llm_agent import LLMAgent
from utils.logger import setup_logger

console = Console()


class PhishScopeCLI:
    """Enhanced CLI with Rich formatting"""
    
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
        
    async def analyze(self) -> Dict[str, Any]:
        """Run complete phishing analysis with Rich UI"""
        
        # Display header
        console.print()
        console.print(Panel.fit(
            "[bold cyan]🔍 PhishScope[/bold cyan]\n"
            "[dim]Evidence-Driven Phishing Analysis Agent[/dim]",
            border_style="cyan"
        ))
        console.print()
        
        # Display URL
        console.print(f"[bold]Target URL:[/bold] [link]{self.url}[/link]")
        console.print(f"[bold]Output Directory:[/bold] {self.output_dir}")
        console.print()
        
        results = {
            "url": self.url,
            "timestamp": datetime.utcnow().isoformat(),
            "findings": {}
        }
        
        try:
            # Progress bar for analysis
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                console=console
            ) as progress:
                
                # Step 1: Load page
                task1 = progress.add_task("[cyan]Loading page...", total=100)
                page_data = await self.page_loader.load_page(self.url, self.output_dir)
                page_context = page_data.pop("page_context", None)
                results["page_load"] = page_data
                progress.update(task1, completed=100)
                
                if not page_data.get("success"):
                    console.print("[red]✗[/red] Page load failed")
                    results["error"] = "Page load failed"
                    return results
                
                console.print(f"[green]✓[/green] Page loaded: [bold]{page_data.get('title', 'Unknown')}[/bold]")
                
                # Step 2: DOM inspection
                task2 = progress.add_task("[cyan]Inspecting DOM...", total=100)
                dom_findings = await self.dom_inspector.inspect(page_context, self.output_dir)
                results["findings"]["dom"] = dom_findings
                progress.update(task2, completed=100)
                console.print(f"[green]✓[/green] DOM inspection complete: {len(dom_findings.get('evidence', []))} findings")
                
                # Step 3: JavaScript analysis
                task3 = progress.add_task("[cyan]Analyzing JavaScript...", total=100)
                js_findings = await self.js_inspector.analyze(page_context, self.output_dir)
                results["findings"]["javascript"] = js_findings
                progress.update(task3, completed=100)
                console.print(f"[green]✓[/green] JavaScript analysis complete: {len(js_findings.get('suspicious_patterns', []))} patterns found")
                
                # Step 4: Network analysis
                task4 = progress.add_task("[cyan]Analyzing network traffic...", total=100)
                network_findings = await self.network_inspector.analyze(
                    page_data.get("network_log", []),
                    self.output_dir
                )
                results["findings"]["network"] = network_findings
                progress.update(task4, completed=100)
                console.print(f"[green]✓[/green] Network analysis complete: {len(network_findings.get('exfiltration_candidates', []))} exfiltration candidates")
                
                # Step 5: AI analysis (optional)
                if self.llm_agent and self.llm_agent.is_available():
                    task5 = progress.add_task("[cyan]Running AI analysis...", total=100)
                    ai_findings = self.llm_agent.analyze(
                        {
                            'dom': dom_findings,
                            'javascript': js_findings,
                            'network': network_findings
                        }
                    )
                    results["findings"]["ai_analysis"] = ai_findings
                    progress.update(task5, completed=100)
                    console.print(f"[green]✓[/green] AI analysis complete: {ai_findings.get('phishing_assessment', {}).get('verdict', 'Unknown')}")
                else:
                    console.print(f"[yellow]⚠[/yellow] AI analysis skipped (not configured)")
                
                # Step 6: Generate report
                task6 = progress.add_task("[cyan]Generating report...", total=100)
                report_path = await self.report_agent.generate_report(results, self.output_dir)
                results["report_path"] = str(report_path)
                progress.update(task6, completed=100)
                console.print(f"[green]✓[/green] Report generated: {report_path}")
            
            # Cleanup
            await self.page_loader.cleanup()
            
            # Display summary
            console.print()
            self.display_summary(results)
            
            # Display findings
            console.print()
            self.display_findings(results)
            
            console.print()
            console.print(Panel.fit(
                f"[bold green]✓ Analysis Complete![/bold green]\n"
                f"[dim]Report saved to: {self.output_dir}[/dim]",
                border_style="green"
            ))
            
        except Exception as e:
            console.print(f"\n[red]✗ Analysis failed:[/red] {str(e)}")
            results["error"] = str(e)
            if self.verbose:
                console.print_exception()
        
        return results
    
    def display_summary(self, results: Dict[str, Any]):
        """Display analysis summary in a table"""
        findings = results.get("findings", {})
        dom = findings.get("dom", {})
        js = findings.get("javascript", {})
        network = findings.get("network", {})
        ai = findings.get("ai_analysis", {})
        
        table = Table(title="📊 Analysis Summary", box=box.ROUNDED, show_header=True, header_style="bold cyan")
        table.add_column("Metric", style="cyan", width=30)
        table.add_column("Value", justify="right", style="bold")
        
        # Add AI verdict if available
        if ai and ai.get('phishing_assessment'):
            assessment = ai['phishing_assessment']
            verdict = assessment.get('verdict', 'Unknown')
            confidence = assessment.get('confidence', 0)
            
            # Color code based on verdict
            if 'High Risk' in verdict:
                verdict_style = "[bold red]"
            elif 'Medium Risk' in verdict:
                verdict_style = "[bold yellow]"
            elif 'Low Risk' in verdict:
                verdict_style = "[bold orange]"
            else:
                verdict_style = "[bold green]"
            
            table.add_row("🤖 AI Verdict", f"{verdict_style}{verdict}[/] ({confidence}%)")
            table.add_row("", "")  # Separator
        
        table.add_row("Forms Detected", str(dom.get("forms_count", 0)))
        table.add_row("Password Fields", str(len(dom.get("password_fields", []))))
        table.add_row("Suspicious JS Patterns", str(len(js.get("suspicious_patterns", []))))
        table.add_row("Exfiltration Endpoints", str(len(network.get("exfiltration_candidates", []))))
        table.add_row("Total Network Requests", str(network.get("total_requests", 0)))
        
        console.print(table)
    
    def display_findings(self, results: Dict[str, Any]):
        """Display detailed findings"""
        findings = results.get("findings", {})
        
        # DOM Findings
        dom = findings.get("dom", {})
        if dom.get("evidence"):
            console.print(Panel(
                "\n".join(f"• {e}" for e in dom["evidence"]),
                title="[bold]🔍 DOM Analysis[/bold]",
                border_style="blue"
            ))
        
        # JavaScript Findings
        js = findings.get("javascript", {})
        if js.get("evidence"):
            console.print(Panel(
                "\n".join(f"• {e}" for e in js["evidence"]),
                title="[bold]📜 JavaScript Analysis[/bold]",
                border_style="yellow"
            ))
        
        # Network Findings
        network = findings.get("network", {})
        if network.get("evidence"):
            console.print(Panel(
                "\n".join(f"• {e}" for e in network["evidence"]),
                title="[bold]🌐 Network Analysis[/bold]",
                border_style="magenta"
            ))
        
        # Exfiltration candidates
        if network.get("exfiltration_candidates"):
            console.print("\n[bold red]⚠️  Potential Data Exfiltration Endpoints:[/bold red]")
            for candidate in network["exfiltration_candidates"][:3]:  # Top 3
                console.print(f"  • [red]{candidate['domain']}[/red] (score: {candidate['suspicious_score']})")
                console.print(f"    Reasons: {', '.join(candidate['reasons'])}")


def main():
    """Enhanced CLI entry point"""
    parser = argparse.ArgumentParser(
        description="PhishScope - Evidence-Driven Phishing Analysis Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  phishscope_cli.py analyze https://suspicious-site.example.com
  phishscope_cli.py analyze https://phishing.test --output ./reports/case001
  phishscope_cli.py analyze https://phishing.test --verbose

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
        phishscope = PhishScopeCLI(args.url, args.output, args.verbose)
        results = asyncio.run(phishscope.analyze())
        
        # Save raw results
        results_file = args.output / "results.json"
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2)
        
        # Exit with appropriate code
        sys.exit(0 if not results.get("error") else 1)


if __name__ == "__main__":
    main()

# Made with Bob
