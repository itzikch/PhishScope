"""
FastAPI application for PhishScope.

Provides REST API endpoints for phishing analysis.
"""

import uuid
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, HttpUrl

from phishscope.workflow.graph import build_graph
from phishscope.workflow.state import WorkflowStatus
from phishscope.config import settings


logger = logging.getLogger(__name__)

# In-memory storage for analysis results (use database in production)
analysis_cache: Dict[str, Dict[str, Any]] = {}

# Workflow graph (compiled once at startup)
workflow_graph = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    global workflow_graph
    logger.info("Starting PhishScope API...")
    workflow_graph = build_graph()
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


# For backwards compatibility with old Flask routes
@app.post("/analyze")
async def analyze_url_compat(request: AnalyzeRequest, background_tasks: BackgroundTasks):
    """Legacy endpoint - redirects to /api/analyze."""
    return await analyze_url(request, background_tasks)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.API_PORT)
