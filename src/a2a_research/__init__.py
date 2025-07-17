"""
A2A Research Package

A demonstration of Application-to-Application (A2A) communication patterns 
for deep research and search workflows.
"""

from .models import A2AMessage, WebSearchResult, SearchQuery, ResearchInsight
from .base_service import A2AService
from .demo import run_web_research_demo

__version__ = "1.0.0"
__all__ = [
    "A2AMessage",
    "WebSearchResult", 
    "SearchQuery",
    "ResearchInsight",
    "A2AService",
    "run_web_research_demo"
]