"""
Core module for PhishScope.

Contains the main analysis components including page loading,
analyzers, and report generation.
"""

from phishscope.core.page_loader import PageLoader
from phishscope.core.report_generator import ReportGenerator
from phishscope.core.phishing_analyzer import PhishingAnalyzer

__all__ = ["PageLoader", "ReportGenerator", "PhishingAnalyzer"]
