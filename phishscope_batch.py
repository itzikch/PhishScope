#!/usr/bin/env python3
"""
PhishScope Batch Analyzer
CLI tool for batch analysis of multiple URLs
"""

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import argparse
import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import List

from agents.page_loader import PageLoaderAgent
from agents.dom_inspector import DOMInspectorAgent
from agents.js_inspector import JavaScriptInspectorAgent
from agents.network_inspector import NetworkInspectorAgent
from agents.report_agent import ReportAgent
from agents.llm_agent import LLMAgent
from agents.enhanced_report_agent import EnhancedReportAgent
from agents.batch_analyzer import BatchAnalyzer, AnalysisStatus
from utils.logger import setup_logger


async def analyze_single_url(url: str, output_dir: Path, verbose: bool = False, 
                             use_ai: bool = True, enhanced: bool = False):
    """Analyze a single URL (used by batch processor)"""
    logger = setup_logger(verbose)
    
    try:
        # Initialize agents
        page_loader = PageLoaderAgent(logger)
        dom_inspector = DOMInspectorAgent(logger)
        js_inspector = JavaScriptInspectorAgent(logger)
        network_inspector = NetworkInspectorAgent(logger)
        report_agent = ReportAgent(logger)
        
        enhanced_report_agent = None
        if enhanced:
            enhanced_report_agent = EnhancedReportAgent(logger)
        
        llm_agent = None
        if use_ai:
            llm_agent = LLMAgent(logger)
        
        # Run analysis
        results = {
            "url": url,
            "timestamp": datetime.utcnow().isoformat(),
            "findings": {}
        }
        
        # Load page
        page_data = await page_loader.load_page(url, output_dir)
        page_context = page_data.pop("page_context", None)
        results["page_load"] = page_data
        
        if not page_data.get("success"):
            results["error"] = "Page load failed"
            return results
        
        # DOM inspection
        dom_findings = await dom_inspector.inspect(page_context, output_dir)
        results["findings"]["dom"] = dom_findings
        
        # JavaScript analysis
        js_findings = await js_inspector.analyze(page_context, output_dir)
        results["findings"]["javascript"] = js_findings
        
        # Network analysis
        network_findings = await network_inspector.analyze(
            page_data.get("network_log", []),
            output_dir
        )
        results["findings"]["network"] = network_findings
        
        # AI analysis (optional)
        if llm_agent and llm_agent.is_available():
            ai_findings = llm_agent.analyze({
                'dom': dom_findings,
                'javascript': js_findings,
                'network': network_findings
            })
            results["findings"]["ai_analysis"] = ai_findings
        
        # Generate report
        report_path = await report_agent.generate_report(results, output_dir)
        results["report_path"] = str(report_path)
        
        # Enhanced reporting (optional)
        if enhanced_report_agent:
            enhanced_path = enhanced_report_agent.generate_pdf_report(results, output_dir)
            results["enhanced_report_path"] = str(enhanced_path)
            results["iocs"] = enhanced_report_agent.extract_iocs(results)
            results["mitre_techniques"] = enhanced_report_agent.map_mitre_techniques(results)
        
        # Cleanup
        await page_loader.cleanup()
        
        return results
        
    except Exception as e:
        logger.error(f"Analysis failed for {url}: {str(e)}")
        return {
            "url": url,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


def main():
    """CLI entry point for batch analysis"""
    parser = argparse.ArgumentParser(
        description="PhishScope Batch Analyzer - Analyze multiple URLs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze URLs from file
  phishscope-batch analyze --file urls.txt --output ./reports/batch_001
  
  # Analyze multiple URLs directly
  phishscope-batch analyze --urls https://phish1.com https://phish2.com
  
  # With enhanced reporting
  phishscope-batch analyze --file urls.txt --enhanced
  
  # Generate comparative report
  phishscope-batch compare --input ./reports/batch_001
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze multiple URLs")
    analyze_parser.add_argument(
        "--file", "-f",
        type=Path,
        help="File containing URLs (one per line)"
    )
    analyze_parser.add_argument(
        "--urls", "-u",
        nargs="+",
        help="URLs to analyze (space-separated)"
    )
    analyze_parser.add_argument(
        "--output", "-o",
        type=Path,
        default=None,
        help="Output directory for reports"
    )
    analyze_parser.add_argument(
        "--max-concurrent",
        type=int,
        default=3,
        help="Maximum concurrent analyses (default: 3)"
    )
    analyze_parser.add_argument(
        "--enhanced",
        action="store_true",
        help="Enable enhanced reporting"
    )
    analyze_parser.add_argument(
        "--no-ai",
        action="store_true",
        help="Disable AI analysis"
    )
    analyze_parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    # Compare command
    compare_parser = subparsers.add_parser("compare", help="Generate comparative report")
    compare_parser.add_argument(
        "--input", "-i",
        type=Path,
        required=True,
        help="Directory containing batch analysis results"
    )
    compare_parser.add_argument(
        "--output", "-o",
        type=Path,
        default=None,
        help="Output file for comparative report"
    )
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Handle analyze command
    if args.command == "analyze":
        # Get URLs
        urls = []
        if args.file:
            if not args.file.exists():
                print(f"Error: File not found: {args.file}")
                sys.exit(1)
            with open(args.file, 'r') as f:
                urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        elif args.urls:
            urls = args.urls
        else:
            print("Error: Must specify either --file or --urls")
            sys.exit(1)
        
        if not urls:
            print("Error: No URLs to analyze")
            sys.exit(1)
        
        # Generate output directory
        if args.output is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            args.output = Path(f"./reports/batch_{timestamp}")
        
        args.output.mkdir(parents=True, exist_ok=True)
        
        print(f"🔍 PhishScope Batch Analyzer")
        print(f"=" * 60)
        print(f"URLs to analyze: {len(urls)}")
        print(f"Max concurrent: {args.max_concurrent}")
        print(f"Output directory: {args.output}")
        print(f"Enhanced reporting: {'Yes' if args.enhanced else 'No'}")
        print(f"AI analysis: {'No' if args.no_ai else 'Yes'}")
        print(f"=" * 60)
        print()
        
        # Run batch analysis
        asyncio.run(run_batch_analysis(
            urls,
            args.output,
            args.max_concurrent,
            args.verbose,
            not args.no_ai,
            args.enhanced
        ))
    
    # Handle compare command
    elif args.command == "compare":
        if not args.input.exists():
            print(f"Error: Directory not found: {args.input}")
            sys.exit(1)
        
        if args.output is None:
            args.output = args.input / "comparative_report.json"
        
        print(f"📊 Generating comparative report...")
        print(f"Input directory: {args.input}")
        print(f"Output file: {args.output}")
        
        # Generate comparative report
        generate_comparative_report(args.input, args.output)


async def run_batch_analysis(urls: List[str], output_dir: Path, max_concurrent: int,
                             verbose: bool, use_ai: bool, enhanced: bool):
    """Run batch analysis"""
    logger = setup_logger(verbose)
    batch_analyzer = BatchAnalyzer(logger, max_concurrent)
    
    # Add jobs
    print(f"Adding {len(urls)} URLs to queue...")
    job_ids = batch_analyzer.add_bulk_jobs(urls)
    
    # Create analyzer function
    async def analyzer_func(url, job_output_dir):
        return await analyze_single_url(url, job_output_dir, verbose, use_ai, enhanced)
    
    # Process queue
    print(f"\nProcessing queue...")
    await batch_analyzer.process_queue(analyzer_func)
    
    # Print results
    print(f"\n{'='*60}")
    print(f"Batch Analysis Complete")
    print(f"{'='*60}")
    
    stats = batch_analyzer.get_queue_stats()
    print(f"Total jobs: {stats['total_jobs']}")
    print(f"Completed: {stats['completed']}")
    print(f"Failed: {stats['failed']}")
    print(f"Cancelled: {stats['cancelled']}")
    
    # Generate comparative report
    print(f"\nGenerating comparative report...")
    comparative = batch_analyzer.generate_comparative_report()
    
    comparative_path = output_dir / "comparative_analysis.json"
    with open(comparative_path, 'w') as f:
        json.dump(comparative, f, indent=2)
    
    print(f"Comparative report saved: {comparative_path}")
    
    # Export all results
    export_path = output_dir / "batch_results.json"
    batch_analyzer.export_results(export_path)
    print(f"Batch results exported: {export_path}")
    
    # Print summary
    print(f"\n📊 Risk Summary:")
    print(f"  High Risk: {comparative.get('high_risk_count', 0)} ({comparative.get('high_risk_percentage', 0)}%)")
    print(f"  Medium Risk: {comparative.get('medium_risk_count', 0)} ({comparative.get('medium_risk_percentage', 0)}%)")
    print(f"  Low Risk: {comparative.get('low_risk_count', 0)} ({comparative.get('low_risk_percentage', 0)}%)")
    
    if comparative.get('common_domains'):
        print(f"\n🌐 Most Common Domains:")
        for domain, count in list(comparative['common_domains'].items())[:5]:
            print(f"  {domain}: {count} occurrence(s)")


def generate_comparative_report(input_dir: Path, output_path: Path):
    """Generate comparative report from existing results"""
    # This is a simplified version - in production, would load all results
    print(f"Comparative report generation from directory not yet implemented")
    print(f"Use the batch analyzer's built-in comparative reporting instead")


if __name__ == "__main__":
    main()


# Made with Bob