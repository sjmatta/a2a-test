"""
Data models for A2A research system.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from datetime import datetime


@dataclass
class A2AMessage:
    """Represents a message in A2A communication."""
    id: str
    sender: str
    recipient: str
    payload: Dict[str, Any]
    timestamp: str
    signature: Optional[str] = None


@dataclass
class WebSearchResult:
    """Represents a web search result."""
    id: str
    title: str
    url: str
    snippet: str
    source: str
    search_query: str
    relevance_score: float = 0.0
    extracted_at: str = ""


@dataclass
class SearchQuery:
    """Represents a search query with parameters."""
    id: str
    query_text: str
    max_results: int = 10
    domain_filters: List[str] = field(default_factory=list)


@dataclass
class ResearchInsight:
    """Represents an extracted insight from research."""
    id: str
    content: str
    confidence: float
    source_urls: List[str]
    insight_type: str
    extracted_at: str