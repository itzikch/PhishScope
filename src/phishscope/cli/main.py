#!/usr/bin/env python3
"""
Command line interface for PhishScope - Evidence-Driven Phishing Analysis Agent.

Usage:
    phishscope analyze <url>
    phishscope analyze <url> --output ./reports/case001
    phishscope serve --port 8070
"""

import json
import uuid
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from phishscope.workflow.graph import build_graph
from phishscope.workflow.state import WorkflowStatus
from phishscope.utils.logger import configure_logging


console = Console()
logger = logging.getLogger(__name__)


def print_header():
    """Print CLI header."""
    console.print(
        Panel.fit(
            "[bold cyan]PhishScope[/bold cyan]\n"
            "[dim]Evidence-Driven Phishing Analysis Agent[/dim]",
            border_style="cyan",
        )
    )


def create_initial_state(url: str, output_dir: str) -> dict:
    """
    Create initial workflow state.

    Args:
        url: Target URL to analyze.
        output_dir: Output directory for reports.

    Returns:
        Initial workflow state dictionary.
    """
    return {
        "workflow_id": str(uuid.uuid4()),
        "url": url,
        "output_dir": output_dir,
        "page_load_result": None,
        "network_log": None,
        "dom_findings": None,
        "js_findings": None,
        "network_findings": None,
        "ai_findings": None,
        "report_path": None,
        "status": WorkflowStatus.PENDING.value,
        "start_time": datetime.now().isoformat(),
        "end_time": None,
        "error": None,
    }


def calculate_duration(start_time: str, end_time: str) -> float:
    """Calculate workflow duration in seconds."""
    start = datetime.fromisoformat(start_time)
    end = datetime.fromisoformat(end_time)
    return (end - start).total_seconds()


def build_summary_table(result: dict) -> Table:
    """Build a rich table with analysis summary."""
    table = Table(
        title="Analysis Summary",
        show_header=True,
        header_style="bold magenta",
        box=box.ROUNDED,
    )
    table.add_column("Metric", style="cyan", width=30)
    table.add_column("Value", style="white")

    # AI Assessment
    ai_findings = result.get("ai_findings", {})
    if ai_findings:
        assessment = ai_findings.get("phishing_assessment", {})
        verdict = assessment.get("verdict", "Unknown")
        confidence = assessment.get("confidence", "N/A")

        # Color code verdict
        if "High Risk" in verdict:
            verdict_display = f"[bold red]{verdict}[/bold red]"
        elif "Medium Risk" in verdict:
            verdict_display = f"[bold yellow]{verdict}[/bold yellow]"
        else:
            verdict_display = f"[bold green]{verdict}[/bold green]"

        table.add_row("AI Verdict", f"{verdict_display} ({confidence}%)")
        table.add_row("", "")

    # DOM findings
    dom = result.get("dom_findings", {})
    table.add_row("Forms Detected", str(dom.get("forms_count", 0)))
    table.add_row("Password Fields", str(len(dom.get("password_fields", []))))

    # JavaScript findings
    js = result.get("js_findings", {})
    table.add_row("Suspicious JS Patterns", str(len(js.get("suspicious_patterns", []))))

    # Network findings
    network = result.get("network_findings", {})
    table.add_row("Exfiltration Endpoints", str(len(network.get("exfiltration_candidates", []))))
    table.add_row("Total Network Requests", str(network.get("total_requests", 0)))

    return table


def print_results(result: dict):
    """Print workflow results to console."""
    console.print("\n")

    # Status
    status = result.get("status", "unknown")
    status_color = {"completed": "green", "failed": "red"}.get(status, "yellow")
    console.print(f"Status: [{status_color}]{status.upper()}[/{status_color}]")

    if result.get("error"):
        console.print(f"\n[red]Error: {result['error']}[/red]\n")
        return

    # Duration
    if result.get("end_time") and result.get("start_time"):
        duration = calculate_duration(result["start_time"], result["end_time"])
        console.print(f"Duration: [cyan]{duration:.2f}[/cyan] seconds")

    # Summary table
    console.print("\n")
    summary_table = build_summary_table(result)
    console.print(summary_table)

    # Key findings from AI
    ai_findings = result.get("ai_findings", {})
    if ai_findings:
        assessment = ai_findings.get("phishing_assessment", {})
        indicators = assessment.get("key_indicators", [])
        if indicators:
            console.print("\n[bold]Key Indicators:[/bold]")
            for indicator in indicators:
                console.print(f"  - {indicator}")

        reasoning = assessment.get("reasoning", "")
        if reasoning:
            console.print(f"\n[bold]Assessment:[/bold] {reasoning.strip()}")

    # Report location
    if result.get("report_path"):
        console.print(f"\n[bold green]Report saved to:[/bold green] {result['report_path']}")

    console.print("\n[bold green]Analysis completed[/bold green]\n")


def save_results_json(result: dict, output_path: Path):
    """Save workflow results to JSON file."""
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False, default=str)
    console.print(f"\n[green]Results saved to:[/green] {output_path}")


@click.group()
@click.version_option(version="0.1.0", prog_name="phishscope")
def cli():
    """PhishScope - Evidence-Driven Phishing Analysis Agent.

    Analyzes web pages for phishing indicators using Playwright browser automation
    and optional LLM-powered analysis.

    Security Warning:
        PhishScope loads potentially malicious content. Always run in an isolated
        environment (VM or container) with proper network controls.
    """


@cli.command()
@click.argument("url")
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output directory for reports (default: ./reports/case_TIMESTAMP)",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose logging",
)
def analyze(url: str, output: Optional[str], verbose: bool):
    """Analyze a URL for phishing indicators.

    Example:
        phishscope analyze https://suspicious-site.example.com
        phishscope analyze https://phishing.test --output ./reports/case001
    """
    import asyncio

    configure_logging(verbose)
    print_header()

    # Validate URL
    if not url.startswith("http://") and not url.startswith("https://"):
        console.print("[red]Error: URL must start with http:// or https://[/red]")
        raise click.Abort()

    # Generate output directory if not specified
    if output is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output = f"./reports/case_{timestamp}"

    output_dir = Path(output)
    output_dir.mkdir(parents=True, exist_ok=True)

    console.print(f"\n[bold]Analyzing:[/bold] [blue]{url}[/blue]")
    console.print(f"[bold]Output:[/bold] {output_dir}\n")

    # Build workflow graph
    graph = build_graph()

    # Create initial state
    initial_state = create_initial_state(url=url, output_dir=str(output_dir))

    # Execute workflow with spinner
    try:
        with console.status("[bold green]Running analysis...", spinner="dots"):
            # Run async workflow
            result = asyncio.get_event_loop().run_until_complete(
                _run_workflow_async(graph, initial_state)
            )
    except Exception as e:
        console.print(f"\n[red]Analysis failed: {e}[/red]\n")
        logger.exception("Workflow execution failed")
        raise click.Abort()

    # Print results
    print_results(result)

    # Save results JSON
    results_path = output_dir / "results.json"
    save_results_json(result, results_path)


async def _run_workflow_async(graph, initial_state: dict) -> dict:
    """Run the workflow graph asynchronously."""
    result = await graph.ainvoke(initial_state)
    return result


@cli.command()
@click.option(
    "--host",
    default="0.0.0.0",
    help="Host to bind the API server to (default: 0.0.0.0)",
)
@click.option(
    "--port",
    default=8070,
    type=int,
    help="Port to bind the API server to (default: 8070)",
)
@click.option(
    "--reload",
    is_flag=True,
    help="Enable auto-reload for development",
)
def serve(host: str, port: int, reload: bool):
    """Start the FastAPI server.

    Example:
        phishscope serve
        phishscope serve --port 8080 --reload
    """
    import uvicorn

    console.print(
        Panel.fit(
            f"[bold cyan]Starting PhishScope API Server[/bold cyan]\n"
            f"[white]Host:[/white] [green]{host}[/green]\n"
            f"[white]Port:[/white] [green]{port}[/green]\n"
            f"[white]Reload:[/white] [green]{'Enabled' if reload else 'Disabled'}[/green]",
            border_style="cyan",
        )
    )

    console.print(
        f"\n[bold green]Server running at [blue]http://{host}:{port}[/blue]"
    )
    console.print("[dim]Press CTRL+C to stop[/dim]\n")

    uvicorn.run(
        "phishscope.api.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )


@cli.command()
def version():
    """Show version information."""
    console.print("[cyan]PhishScope[/cyan] version [green]0.1.0[/green]")


def main():
    """Main entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
