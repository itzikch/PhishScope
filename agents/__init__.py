"""
PhishScope Analysis Agents
"""

from .page_loader import PageLoaderAgent
from .dom_inspector import DOMInspectorAgent
from .js_inspector import JavaScriptInspectorAgent
from .network_inspector import NetworkInspectorAgent
from .report_agent import ReportAgent

__all__ = [
    "PageLoaderAgent",
    "DOMInspectorAgent",
    "JavaScriptInspectorAgent",
    "NetworkInspectorAgent",
    "ReportAgent",
]

# Made with Bob
