"""
Research aggregation service for A2A research system.
"""

import uuid
from typing import Dict, Any, List
from datetime import datetime
from collections import defaultdict

from .base_service import A2AService
from .models import A2AMessage


class WebResearchAggregationService(A2AService):
    """Service for aggregating web research results and generating comprehensive reports."""
    
    def __init__(self, shared_secret: str):
        super().__init__("web-research-aggregation", shared_secret)
        self.research_sessions: Dict[str, Dict[str, Any]] = {}
        
        self._register_handlers()
    
    def _register_handlers(self):
        """Register message handlers for this service."""
        self.register_handler('start_web_research_session', self.handle_start_session)
        self.register_handler('aggregate_web_results', self.handle_aggregate_results)
        self.register_handler('generate_web_report', self.handle_generate_report)
    
    async def handle_start_session(self, message: A2AMessage):
        """Handle web research session initialization."""
        session_data = message.payload.get('session', {})
        session_id = session_data.get('id', str(uuid.uuid4()))
        
        self.research_sessions[session_id] = {
            'id': session_id,
            'topic': session_data.get('topic', 'Unknown'),
            'started_at': datetime.utcnow().isoformat(),
            'search_results': [],
            'insights': [],
            'queries': [],
            'sources_analyzed': 0
        }
        
        print(f"[{self.service_name}] Started web research session: {session_data.get('topic')} ({session_id})")
    
    async def handle_aggregate_results(self, message: A2AMessage):
        """Handle web result aggregation requests."""
        session_id = message.payload.get('session_id')
        results = message.payload.get('results', [])
        
        if session_id in self.research_sessions:
            session = self.research_sessions[session_id]
            session['search_results'].extend(results)
            session['sources_analyzed'] += len(results)
            print(f"[{self.service_name}] Aggregated {len(results)} web results for session {session_id}")
    
    async def handle_generate_report(self, message: A2AMessage):
        """Handle web research report generation requests."""
        session_id = message.payload.get('session_id')
        
        if session_id in self.research_sessions:
            session = self.research_sessions[session_id]
            report = self._generate_web_research_report(session)
            print(f"[{self.service_name}] Generated web research report for: {session['topic']}")
            print(f"[{self.service_name}] Report summary: {session['sources_analyzed']} web sources analyzed")
    
    def _generate_web_research_report(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a comprehensive web research report."""
        search_results = session.get('search_results', [])
        
        # Extract domains from URLs
        domains = set()
        for result in search_results:
            url = result.get('url', '')
            if url:
                domain = self._extract_domain(url)
                domains.add(domain)
        
        report = {
            'session_id': session['id'],
            'topic': session['topic'],
            'generated_at': datetime.utcnow().isoformat(),
            'total_sources': len(search_results),
            'unique_domains': len(domains),
            'top_domains': list(domains)[:5],
            'average_relevance': self._calculate_avg_relevance(search_results),
            'source_types': self._categorize_sources(search_results),
            'research_coverage': self._assess_coverage(search_results)
        }
        
        return report
    
    def _calculate_avg_relevance(self, search_results: List[Dict[str, Any]]) -> float:
        """Calculate average relevance score of search results."""
        if not search_results:
            return 0.0
        
        total_relevance = sum(result.get('relevance_score', 0.0) for result in search_results)
        return total_relevance / len(search_results)
    
    def _categorize_sources(self, search_results: List[Dict[str, Any]]) -> Dict[str, int]:
        """Categorize sources by type."""
        categories = {
            'academic': 0,
            'government': 0,
            'commercial': 0,
            'news': 0,
            'other': 0
        }
        
        for result in search_results:
            url = result.get('url', '').lower()
            source = result.get('source', '').lower()
            
            if any(term in url or term in source for term in ['nature', 'science', 'ieee', 'arxiv', 'pubmed']):
                categories['academic'] += 1
            elif '.gov' in url or 'nist' in source:
                categories['government'] += 1
            elif any(term in url for term in ['.com', '.org']):
                categories['commercial'] += 1
            elif any(term in source for term in ['news', 'times', 'post', 'journal']):
                categories['news'] += 1
            else:
                categories['other'] += 1
        
        return categories
    
    def _assess_coverage(self, search_results: List[Dict[str, Any]]) -> str:
        """Assess the comprehensiveness of research coverage."""
        if len(search_results) >= 10:
            return "Comprehensive"
        elif len(search_results) >= 5:
            return "Moderate"
        else:
            return "Limited"
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        if not url:
            return ''
        parts = url.split('/')
        return parts[2] if len(parts) > 2 else url