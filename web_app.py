#!/usr/bin/env python3
"""
PhishScope Web Application
Flask-based web interface for PhishScope analysis
"""

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, will use system environment variables

import asyncio
import json
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS

from agents.page_loader import PageLoaderAgent
from agents.dom_inspector import DOMInspectorAgent
from agents.js_inspector import JavaScriptInspectorAgent
from agents.network_inspector import NetworkInspectorAgent
from agents.llm_agent import LLMAgent
from agents.report_agent import ReportAgent
from utils.logger import setup_logger

app = Flask(__name__)
CORS(app)

# Setup logger
logger = setup_logger(verbose=True, name="phishscope-web")

# Store for analysis results (in production, use a database)
analysis_cache = {}


class PhishScopeWeb:
    """Web interface wrapper for PhishScope"""
    
    def __init__(self):
        self.logger = logger
        
    async def analyze_url(self, url: str, output_dir: Path) -> dict:
        """Run PhishScope analysis on a URL"""
        
        results = {
            "url": url,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "running",
            "findings": {}
        }
        
        try:
            # Initialize agents
            page_loader = PageLoaderAgent(self.logger)
            dom_inspector = DOMInspectorAgent(self.logger)
            js_inspector = JavaScriptInspectorAgent(self.logger)
            network_inspector = NetworkInspectorAgent(self.logger)
            report_agent = ReportAgent(self.logger)
            llm_agent = LLMAgent(self.logger)
            
            # Step 1: Load page
            self.logger.info(f"[1/5] Loading page: {url}")
            page_data = await page_loader.load_page(url, output_dir)
            page_context = page_data.pop("page_context", None)
            results["page_load"] = page_data
            
            if not page_data.get("success"):
                results["status"] = "error"
                results["error"] = "Page load failed"
                return results
            
            # Step 2: DOM inspection
            self.logger.info("[2/5] Inspecting DOM...")
            dom_findings = await dom_inspector.inspect(page_context, output_dir)
            results["findings"]["dom"] = dom_findings
            
            # Step 3: JavaScript analysis
            self.logger.info("[3/5] Analyzing JavaScript...")
            js_findings = await js_inspector.analyze(page_context, output_dir)
            results["findings"]["javascript"] = js_findings
            
            # Step 4: Network analysis
            self.logger.info("[4/5] Analyzing network traffic...")
            network_findings = await network_inspector.analyze(
                page_data.get("network_log", []),
                output_dir
            )
            results["findings"]["network"] = network_findings
            
            # Step 5: AI analysis (optional)
            if llm_agent.is_available():
                self.logger.info("[5/6] Running AI analysis...")
                ai_findings = llm_agent.analyze({
                    'dom': dom_findings,
                    'javascript': js_findings,
                    'network': network_findings
                })
                results["findings"]["ai_analysis"] = ai_findings
            else:
                self.logger.info("[5/6] AI analysis skipped (not configured)")
            
            # Step 6: Generate report
            self.logger.info("[6/6] Generating report...")
            report_path = await report_agent.generate_report(results, output_dir)
            results["report_path"] = str(report_path)
            
            # Cleanup
            await page_loader.cleanup()
            
            results["status"] = "complete"
            self.logger.info("Analysis complete")
            
        except Exception as e:
            self.logger.error(f"Analysis failed: {str(e)}", exc_info=True)
            results["status"] = "error"
            results["error"] = str(e)
        
        return results


phishscope = PhishScopeWeb()


@app.route('/')
def index():
    """Serve the main web interface"""
    return render_template('index.html')


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """API endpoint to analyze a URL"""
    data = request.get_json()
    url = data.get('url')
    
    if not url:
        return jsonify({"error": "URL is required"}), 400
    
    if not url.startswith('http://') and not url.startswith('https://'):
        return jsonify({"error": "URL must start with http:// or https://"}), 400
    
    # Generate unique analysis ID
    analysis_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    output_dir = Path(f"./reports/web_{analysis_id}")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Run analysis in background
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        results = loop.run_until_complete(phishscope.analyze_url(url, output_dir))
        loop.close()
        
        # Cache results
        analysis_cache[analysis_id] = results
        
        return jsonify({
            "analysis_id": analysis_id,
            "status": results["status"],
            "results": results
        })
        
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route('/api/results/<analysis_id>')
def get_results(analysis_id):
    """Get analysis results by ID"""
    if analysis_id not in analysis_cache:
        return jsonify({"error": "Analysis not found"}), 404
    
    return jsonify(analysis_cache[analysis_id])


@app.route('/api/screenshot/<analysis_id>')
def get_screenshot(analysis_id):
    """Serve screenshot for an analysis"""
    screenshot_path = Path(f"./reports/web_{analysis_id}/screenshot.png")
    if screenshot_path.exists():
        return send_from_directory(screenshot_path.parent, screenshot_path.name)
    return jsonify({"error": "Screenshot not found"}), 404


@app.route('/api/report/<analysis_id>')
def get_report(analysis_id):
    """Get markdown report for an analysis"""
    report_path = Path(f"./reports/web_{analysis_id}/report.md")
    if report_path.exists():
        with open(report_path, 'r') as f:
            return jsonify({"report": f.read()})
    return jsonify({"error": "Report not found"}), 404


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "PhishScope Web"})


if __name__ == '__main__':
    print("=" * 60)
    print("🔍 PhishScope Web Application")
    print("=" * 60)
    print("")
    print("Starting server on http://localhost:8070")
    print("")
    print("API Endpoints:")
    print("  POST /api/analyze       - Analyze a URL")
    print("  GET  /api/results/<id>  - Get analysis results")
    print("  GET  /api/screenshot/<id> - Get screenshot")
    print("  GET  /api/report/<id>   - Get markdown report")
    print("")
    print("⚠️  Warning: This will load potentially malicious URLs")
    print("   Only use in an isolated environment!")
    print("")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=8070, debug=True)

# Made with Bob
