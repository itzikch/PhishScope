"""
Workflow module for PhishScope.

Implements the LangGraph-based analysis workflow.
"""

from phishscope.workflow.graph import build_graph
from phishscope.workflow.state import WorkflowState, WorkflowStatus

__all__ = ["build_graph", "WorkflowState", "WorkflowStatus"]
