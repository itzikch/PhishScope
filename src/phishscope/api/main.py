"""
FastAPI application for PhishScope.

Provides REST API endpoints for phishing analysis.
"""

import uuid
import logging
import json
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel, HttpUrl

from phishscope.workflow.graph import build_graph
from phishscope.workflow.state import WorkflowStatus
from phishscope.config import settings
from phishscope.agents.virustotal_agent import VirusTotalAgent
from phishscope.core.page_loader import PageLoader
from phishscope.core.analyzers.dom import DOMAnalyzer
from phishscope.core.analyzers.javascript import JavaScriptAnalyzer
from phishscope.core.analyzers.network import NetworkAnalyzer
from phishscope.llm.clients import get_chat_llm_client, is_llm_available
from phishscope.llm.debate_orchestrator import DebateOrchestrator


logger = logging.getLogger(__name__)

# In-memory storage for analysis results (use database in production)
analysis_cache: Dict[str, Dict[str, Any]] = {}

# Workflow graph (compiled once at startup)
workflow_graph = None
vt_agent = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    global workflow_graph, vt_agent
    logger.info("Starting PhishScope API...")
    workflow_graph = build_graph()
    
    if settings.VIRUSTOTAL_API_KEY:
        vt_agent = VirusTotalAgent(settings.VIRUSTOTAL_API_KEY)
        logger.info("VirusTotal integration enabled")
    else:
        logger.warning("VIRUSTOTAL_API_KEY not set, VT integration disabled")
        
    yield
    logger.info("Shutting down PhishScope API...")


app = FastAPI(
    title="PhishScope API",
    description="Evidence-Driven Phishing Analysis Agent",
    version="0.1.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response models
class AnalyzeRequest(BaseModel):
    """Request model for URL analysis."""
    url: HttpUrl

    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://example.com"
            }
        }


class AnalysisResponse(BaseModel):
    """Response model for analysis results."""
    analysis_id: str
    status: str
    url: str
    message: Optional[str] = None


class AnalysisResult(BaseModel):
    """Full analysis result model."""
    analysis_id: str
    status: str
    url: str
    timestamp: Optional[str] = None
    findings: Optional[Dict[str, Any]] = None
    report_path: Optional[str] = None
    error: Optional[str] = None


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "PhishScope API", "version": "0.1.0"}


class VirusTotalScanRequest(BaseModel):
    url: HttpUrl

@app.post("/api/virustotal/scan")
async def scan_url_vt(request: VirusTotalScanRequest):
    """Submit URL to VirusTotal for scanning."""
    if not vt_agent:
        raise HTTPException(status_code=503, detail="VirusTotal integration not configured")
    
    try:
        result = await vt_agent.scan_url(str(request.url))
        return result
    except Exception as e:
        logger.error(f"VirusTotal scan error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/virustotal/report")
async def get_vt_report(url: str):
    """Get VirusTotal analysis report for URL."""
    if not vt_agent:
        raise HTTPException(status_code=503, detail="VirusTotal integration not configured")
    
    try:
        # Check if url parameter is provided
        if not url:
            raise HTTPException(status_code=400, detail="URL parameter required")
            
        result = await vt_agent.get_url_analysis(url)
        return result
    except Exception as e:
        logger.error(f"VirusTotal report error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_url(request: AnalyzeRequest, background_tasks: BackgroundTasks):
    """
    Analyze a URL for phishing indicators.

    The analysis runs in the background. Use the returned analysis_id
    to poll for results via GET /api/results/{analysis_id}.
    """
    url = str(request.url)
    analysis_id = datetime.now().strftime("%Y%m%d_%H%M%S_") + str(uuid.uuid4())[:8]

    # Validate URL
    if not url.startswith("http://") and not url.startswith("https://"):
        raise HTTPException(
            status_code=400,
            detail="URL must start with http:// or https://"
        )

    # Initialize analysis record
    output_dir = settings.REPORTS_DIR / f"web_{analysis_id}"
    output_dir.mkdir(parents=True, exist_ok=True)

    analysis_cache[analysis_id] = {
        "analysis_id": analysis_id,
        "url": url,
        "output_dir": str(output_dir),
        "status": "running",
        "timestamp": datetime.utcnow().isoformat(),
        "findings": None,
        "report_path": None,
        "error": None,
    }

    # Start background analysis
    background_tasks.add_task(run_analysis, analysis_id, url, str(output_dir))

    return AnalysisResponse(
        analysis_id=analysis_id,
        status="running",
        url=url,
        message="Analysis started. Poll /api/results/{analysis_id} for results."
    )


async def run_analysis(analysis_id: str, url: str, output_dir: str):
    """Run the analysis workflow in the background."""
    try:
        logger.info(f"Starting analysis {analysis_id} for URL: {url}")

        # Create initial state
        initial_state = {
            "workflow_id": analysis_id,
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

        # Run workflow
        result = await workflow_graph.ainvoke(initial_state)

        # Log the result keys for debugging
        logger.debug(f"Workflow result keys: {list(result.keys())}")
        logger.debug(f"DOM findings present: {result.get('dom_findings') is not None}")
        logger.debug(f"JS findings present: {result.get('js_findings') is not None}")
        logger.debug(f"Network findings present: {result.get('network_findings') is not None}")

        # Update cache with results
        analysis_cache[analysis_id].update({
            "status": result.get("status", "completed"),
            "findings": {
                "dom": result.get("dom_findings"),
                "javascript": result.get("js_findings"),
                "network": result.get("network_findings"),
                "ai_analysis": result.get("ai_findings"),
            },
            "page_load": result.get("page_load_result"),
            "report_path": result.get("report_path"),
            "error": result.get("error"),
        })

        logger.info(f"Analysis {analysis_id} completed with status: {result.get('status')}")
        
        # Log findings summary for debugging
        findings = analysis_cache[analysis_id].get("findings", {})
        logger.debug(f"Cached findings - DOM: {findings.get('dom') is not None}, "
                    f"JS: {findings.get('javascript') is not None}, "
                    f"Network: {findings.get('network') is not None}")

    except Exception as e:
        logger.exception(f"Analysis {analysis_id} failed")
        analysis_cache[analysis_id].update({
            "status": "failed",
            "error": str(e),
        })


@app.get("/api/results/{analysis_id}")
async def get_results(analysis_id: str):
    """Get analysis results by ID."""
    if analysis_id not in analysis_cache:
        raise HTTPException(status_code=404, detail="Analysis not found")

    return analysis_cache[analysis_id]


@app.get("/api/screenshot/{analysis_id}")
async def get_screenshot(analysis_id: str):
    """Get screenshot for an analysis."""
    if analysis_id not in analysis_cache:
        raise HTTPException(status_code=404, detail="Analysis not found")

    output_dir = analysis_cache[analysis_id].get("output_dir")
    if not output_dir:
        raise HTTPException(status_code=404, detail="Output directory not found")

    screenshot_path = Path(output_dir) / "screenshot.png"
    if not screenshot_path.exists():
        raise HTTPException(status_code=404, detail="Screenshot not found")

    return FileResponse(screenshot_path, media_type="image/png")


@app.get("/api/report/{analysis_id}")
async def get_report(analysis_id: str):
    """Get markdown report for an analysis."""
    if analysis_id not in analysis_cache:
        raise HTTPException(status_code=404, detail="Analysis not found")

    output_dir = analysis_cache[analysis_id].get("output_dir")
    if not output_dir:
        raise HTTPException(status_code=404, detail="Output directory not found")

    report_path = Path(output_dir) / "report.md"
    if not report_path.exists():
        raise HTTPException(status_code=404, detail="Report not found")

    with open(report_path, "r", encoding="utf-8") as f:
        report_content = f.read()

    return {"report": report_content}


@app.get("/api/analyses")
async def list_analyses(limit: int = 20):
    """List recent analyses."""
    analyses = list(analysis_cache.values())
    # Sort by timestamp descending
    analyses.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return {"analyses": analyses[:limit], "total": len(analyses)}

class DebateAnalyzeRequest(BaseModel):
    """Request model for debate-mode URL analysis."""
    url: HttpUrl
    debate_mode: bool = True

    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://example.com",
                "debate_mode": True
            }
        }


@app.post("/api/analyze/debate")
async def analyze_url_debate_stream(request: DebateAnalyzeRequest):
    """
    Analyze a URL using multi-agent debate with Server-Sent Events streaming.
    
    Returns a stream of events:
    - scrape_done: Page scraping completed
    - agent: Each agent's response (prosecutor, defense, judge)
    - verdict: Final verdict from judge
    - done: Analysis complete
    - error: If something goes wrong
    
    The client should connect with EventSource or fetch with streaming.
    """
    url = str(request.url)
    
    # Validate URL
    if not url.startswith("http://") and not url.startswith("https://"):
        raise HTTPException(
            status_code=400,
            detail="URL must start with http:// or https://"
        )
    
    # Check if LLM is available
    if not is_llm_available():
        raise HTTPException(
            status_code=503,
            detail="LLM service not available. Debate mode requires AI capabilities."
        )
    
    async def event_generator():
        """Generate SSE events for the debate analysis."""
        page_loader = None
        
        try:
            # Initialize components
            page_loader = PageLoader()
            dom_analyzer = DOMAnalyzer()
            js_analyzer = JavaScriptAnalyzer()
            network_analyzer = NetworkAnalyzer()
            llm_client = get_chat_llm_client()
            debate_orchestrator = DebateOrchestrator(llm_client)
            
            # Create output directory
            analysis_id = datetime.now().strftime("%Y%m%d_%H%M%S_") + str(uuid.uuid4())[:8]
            output_dir = settings.REPORTS_DIR / f"debate_{analysis_id}"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Step 1: Load page
            logger.info(f"[Debate] Loading page: {url}")
            page_data = await page_loader.load_page(url, output_dir)
            page_context = page_data.pop("page_context", None)
            
            if not page_data.get("success"):
                yield f"event: error\ndata: {json.dumps({'message': 'Failed to load page'})}\n\n"
                return
            
            # Step 2: Run analyzers
            logger.info("[Debate] Running analyzers...")
            dom_findings = await dom_analyzer.analyze(page=page_context, output_dir=output_dir)
            js_findings = await js_analyzer.analyze(page=page_context, output_dir=output_dir)
            network_findings = await network_analyzer.analyze(
                network_log=page_data.get("network_log", []),
                output_dir=output_dir
            )
            
            # Step 3: Stream debate
            logger.info("[Debate] Starting debate stream...")
            async for event in debate_orchestrator.run_debate_streaming(
                url=url,
                page_load=page_data,
                dom_findings=dom_findings,
                js_findings=js_findings,
                network_findings=network_findings
            ):
                event_type = event.get("event", "message")
                event_data = event.get("data", {})
                
                # Format as SSE
                yield f"event: {event_type}\ndata: {json.dumps(event_data)}\n\n"
                
                # Small delay to ensure client receives events in order
                await asyncio.sleep(0.1)
            
            logger.info(f"[Debate] Analysis complete: {analysis_id}")
            
        except Exception as e:
            logger.error(f"[Debate] Stream error: {e}", exc_info=True)
            yield f"event: error\ndata: {json.dumps({'message': str(e)})}\n\n"
        
        finally:
            # Cleanup browser resources
            if page_loader:
                await page_loader.cleanup()
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        }
    )



# For backwards compatibility with old Flask routes
@app.post("/analyze")
async def analyze_url_compat(request: AnalyzeRequest, background_tasks: BackgroundTasks):
    """Legacy endpoint - redirects to /api/analyze."""
    return await analyze_url(request, background_tasks)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.API_PORT)
