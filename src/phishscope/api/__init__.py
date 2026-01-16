"""
API module for PhishScope.

Provides FastAPI-based REST API for phishing analysis.
"""

from phishscope.api.main import app

__all__ = ["app"]
