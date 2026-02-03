"""
BatchAnalyzer - Batch analysis with queue management and comparative reporting
"""

import asyncio
import logging
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum


class AnalysisStatus(Enum):
    """Status of an analysis job"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class AnalysisJob:
    """Represents a single analysis job"""
    job_id: str
    url: str
    status: AnalysisStatus
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    output_dir: Optional[str] = None
    error: Optional[str] = None
    results: Optional[Dict[str, Any]] = None
    priority: int = 0  # Higher number = higher priority
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['status'] = self.status.value
        return data


class BatchAnalyzer:
    """
    Batch analysis capabilities:
    - Queue management for multiple URLs
    - Concurrent analysis with rate limiting
    - Progress tracking
    - Comparative reporting
    - Bulk export
    """
    
    def __init__(self, logger: logging.Logger, max_concurrent: int = 3):
        self.logger = logger
        self.max_concurrent = max_concurrent
        self.jobs: Dict[str, AnalysisJob] = {}
        self.queue: asyncio.Queue = asyncio.Queue()
        self.running_jobs: List[str] = []
        self.lock = asyncio.Lock()
    
    def add_job(self, url: str, priority: int = 0) -> str:
        """
        Add a URL to the analysis queue
        
        Args:
            url: URL to analyze
            priority: Job priority (higher = processed first)
            
        Returns:
            Job ID
        """
        job_id = f"job_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        job = AnalysisJob(
            job_id=job_id,
            url=url,
            status=AnalysisStatus.PENDING,
            created_at=datetime.utcnow().isoformat(),
            priority=priority
        )
        
        self.jobs[job_id] = job
        self.logger.info(f"Added job {job_id} for URL: {url}")
        
        return job_id
    
    def add_bulk_jobs(self, urls: List[str], priority: int = 0) -> List[str]:
        """
        Add multiple URLs to the queue
        
        Args:
            urls: List of URLs to analyze
            priority: Priority for all jobs
            
        Returns:
            List of job IDs
        """
        job_ids = []
        for url in urls:
            job_id = self.add_job(url, priority)
            job_ids.append(job_id)
        
        self.logger.info(f"Added {len(job_ids)} jobs to queue")
        return job_ids
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific job"""
        job = self.jobs.get(job_id)
        if job:
            return job.to_dict()
        return None
    
    def get_all_jobs(self, status_filter: Optional[AnalysisStatus] = None) -> List[Dict[str, Any]]:
        """
        Get all jobs, optionally filtered by status
        
        Args:
            status_filter: Filter by status (None = all jobs)
            
        Returns:
            List of job dictionaries
        """
        jobs = list(self.jobs.values())
        
        if status_filter:
            jobs = [j for j in jobs if j.status == status_filter]
        
        # Sort by priority (desc) then created_at (asc)
        jobs.sort(key=lambda j: (-j.priority, j.created_at))
        
        return [j.to_dict() for j in jobs]
    
    def cancel_job(self, job_id: str) -> bool:
        """Cancel a pending job"""
        job = self.jobs.get(job_id)
        if job and job.status == AnalysisStatus.PENDING:
            job.status = AnalysisStatus.CANCELLED
            self.logger.info(f"Cancelled job {job_id}")
            return True
        return False
    
    async def process_queue(self, analyzer_func):
        """
        Process the job queue with concurrent execution
        
        Args:
            analyzer_func: Async function that takes (url, output_dir) and returns results
        """
        self.logger.info(f"Starting queue processor (max concurrent: {self.max_concurrent})")
        
        # Get pending jobs sorted by priority
        pending_jobs = [j for j in self.jobs.values() if j.status == AnalysisStatus.PENDING]
        pending_jobs.sort(key=lambda j: (-j.priority, j.created_at))
        
        # Create tasks for concurrent execution
        tasks = []
        for job in pending_jobs[:self.max_concurrent]:
            task = asyncio.create_task(self._process_job(job, analyzer_func))
            tasks.append(task)
        
        # Wait for all tasks to complete
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        
        self.logger.info("Queue processing complete")
    
    async def _process_job(self, job: AnalysisJob, analyzer_func):
        """Process a single job"""
        try:
            # Update status
            async with self.lock:
                job.status = AnalysisStatus.RUNNING
                job.started_at = datetime.utcnow().isoformat()
                self.running_jobs.append(job.job_id)
            
            self.logger.info(f"Processing job {job.job_id}: {job.url}")
            
            # Create output directory
            output_dir = Path(f"./reports/batch_{job.job_id}")
            output_dir.mkdir(parents=True, exist_ok=True)
            job.output_dir = str(output_dir)
            
            # Run analysis
            results = await analyzer_func(job.url, output_dir)
            
            # Update job with results
            async with self.lock:
                job.status = AnalysisStatus.COMPLETED
                job.completed_at = datetime.utcnow().isoformat()
                job.results = results
                self.running_jobs.remove(job.job_id)
            
            self.logger.info(f"Completed job {job.job_id}")
            
        except Exception as e:
            self.logger.error(f"Job {job.job_id} failed: {str(e)}")
            async with self.lock:
                job.status = AnalysisStatus.FAILED
                job.completed_at = datetime.utcnow().isoformat()
                job.error = str(e)
                if job.job_id in self.running_jobs:
                    self.running_jobs.remove(job.job_id)
    
    def generate_comparative_report(self, job_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Generate comparative analysis report across multiple jobs
        
        Args:
            job_ids: List of job IDs to compare (None = all completed jobs)
            
        Returns:
            Comparative analysis report
        """
        # Get jobs to compare
        if job_ids:
            jobs = [self.jobs[jid] for jid in job_ids if jid in self.jobs]
        else:
            jobs = [j for j in self.jobs.values() if j.status == AnalysisStatus.COMPLETED]
        
        if not jobs:
            return {"error": "No completed jobs to compare"}
        
        self.logger.info(f"Generating comparative report for {len(jobs)} jobs")
        
        # Aggregate statistics
        stats = {
            "total_analyzed": len(jobs),
            "high_risk_count": 0,
            "medium_risk_count": 0,
            "low_risk_count": 0,
            "common_domains": {},
            "common_techniques": {},
            "total_iocs": 0,
            "jobs": []
        }
        
        all_domains = []
        all_techniques = []
        
        for job in jobs:
            if not job.results:
                continue
            
            findings = job.results.get("findings", {})
            
            # Categorize risk
            risk_level = self._assess_risk_level(findings)
            if risk_level == "high":
                stats["high_risk_count"] += 1
            elif risk_level == "medium":
                stats["medium_risk_count"] += 1
            else:
                stats["low_risk_count"] += 1
            
            # Collect domains
            network = findings.get("network", {})
            for candidate in network.get("exfiltration_candidates", []):
                domain = candidate.get("domain")
                if domain:
                    all_domains.append(domain)
            
            # Add job summary
            stats["jobs"].append({
                "job_id": job.job_id,
                "url": job.url,
                "risk_level": risk_level,
                "forms_count": findings.get("dom", {}).get("forms_count", 0),
                "suspicious_js_patterns": len(findings.get("javascript", {}).get("suspicious_patterns", [])),
                "exfiltration_endpoints": len(network.get("exfiltration_candidates", []))
            })
        
        # Find common domains
        from collections import Counter
        domain_counts = Counter(all_domains)
        stats["common_domains"] = dict(domain_counts.most_common(10))
        
        # Calculate percentages
        total = stats["total_analyzed"]
        if total > 0:
            stats["high_risk_percentage"] = round((stats["high_risk_count"] / total) * 100, 1)
            stats["medium_risk_percentage"] = round((stats["medium_risk_count"] / total) * 100, 1)
            stats["low_risk_percentage"] = round((stats["low_risk_count"] / total) * 100, 1)
        
        return stats
    
    def export_results(self, output_path: Path, job_ids: Optional[List[str]] = None) -> Path:
        """
        Export batch analysis results to JSON
        
        Args:
            output_path: Path to save export file
            job_ids: List of job IDs to export (None = all jobs)
            
        Returns:
            Path to exported file
        """
        # Get jobs to export
        if job_ids:
            jobs = [self.jobs[jid].to_dict() for jid in job_ids if jid in self.jobs]
        else:
            jobs = [j.to_dict() for j in self.jobs.values()]
        
        export_data = {
            "export_date": datetime.utcnow().isoformat(),
            "total_jobs": len(jobs),
            "jobs": jobs,
            "comparative_analysis": self.generate_comparative_report(job_ids)
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2)
        
        self.logger.info(f"Exported {len(jobs)} jobs to {output_path}")
        return output_path
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """Get current queue statistics"""
        return {
            "total_jobs": len(self.jobs),
            "pending": len([j for j in self.jobs.values() if j.status == AnalysisStatus.PENDING]),
            "running": len([j for j in self.jobs.values() if j.status == AnalysisStatus.RUNNING]),
            "completed": len([j for j in self.jobs.values() if j.status == AnalysisStatus.COMPLETED]),
            "failed": len([j for j in self.jobs.values() if j.status == AnalysisStatus.FAILED]),
            "cancelled": len([j for j in self.jobs.values() if j.status == AnalysisStatus.CANCELLED]),
            "max_concurrent": self.max_concurrent,
            "currently_running": len(self.running_jobs)
        }
    
    def clear_completed_jobs(self) -> int:
        """Remove completed jobs from memory"""
        completed_ids = [jid for jid, job in self.jobs.items() 
                        if job.status in [AnalysisStatus.COMPLETED, AnalysisStatus.FAILED, AnalysisStatus.CANCELLED]]
        
        for jid in completed_ids:
            del self.jobs[jid]
        
        self.logger.info(f"Cleared {len(completed_ids)} completed jobs")
        return len(completed_ids)
    
    def _assess_risk_level(self, findings: Dict[str, Any]) -> str:
        """Assess risk level based on findings"""
        score = 0
        
        dom = findings.get("dom", {})
        js = findings.get("javascript", {})
        network = findings.get("network", {})
        
        if dom.get("forms_count", 0) > 0:
            score += 25
        if len(dom.get("password_fields", [])) > 0:
            score += 25
        if len(js.get("suspicious_patterns", [])) >= 3:
            score += 25
        if len(network.get("exfiltration_candidates", [])) > 0:
            score += 25
        
        if score >= 75:
            return "high"
        elif score >= 50:
            return "medium"
        else:
            return "low"


# Made with Bob