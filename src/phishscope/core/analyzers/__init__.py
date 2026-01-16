"""
Phishing Page Analyzer Base Classes

This module provides the base classes and common interfaces for analyzing
web pages for phishing indicators and suspicious behavior.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from pathlib import Path
from playwright.async_api import Page


class BaseAnalyzer(ABC):
    """
    Abstract base class for all phishing page analyzers.

    Analyzers examine different aspects of web pages to identify
    phishing indicators, suspicious behavior, and data exfiltration attempts.
    """

    def __init__(self, name: str):
        """
        Initialize the analyzer.

        Args:
            name: Name of the analyzer
        """
        self.name = name

    @abstractmethod
    async def analyze(
        self,
        page: Optional[Page] = None,
        network_log: Optional[List[Dict[str, Any]]] = None,
        output_dir: Optional[Path] = None,
    ) -> Dict[str, Any]:
        """
        Analyze a web page for phishing indicators.

        Args:
            page: Playwright Page object (for DOM/JS analysis)
            network_log: Network traffic log (for network analysis)
            output_dir: Directory to save artifacts

        Returns:
            Dictionary containing analysis findings

        Raises:
            Exception: If analysis fails
        """

    def get_name(self) -> str:
        """Get the analyzer name."""
        return self.name

    def __repr__(self) -> str:
        """String representation of the analyzer."""
        return f"{self.__class__.__name__}(name='{self.name}')"


# Import concrete analyzers for convenience
from phishscope.core.analyzers.dom import DOMAnalyzer
from phishscope.core.analyzers.javascript import JavaScriptAnalyzer
from phishscope.core.analyzers.network import NetworkAnalyzer

__all__ = ["BaseAnalyzer", "DOMAnalyzer", "JavaScriptAnalyzer", "NetworkAnalyzer"]
