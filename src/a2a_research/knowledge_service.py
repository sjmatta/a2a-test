"""
Knowledge extraction service for A2A research system.
"""

import re
import uuid
from typing import Dict, Any, List
from datetime import datetime
from collections import defaultdict

from .base_service import A2AService
from .models import A2AMessage, ResearchInsight


class WebKnowledgeExtractionService(A2AService):
    """Service for extracting insights and knowledge from web search results."""
    
    def __init__(self, shared_secret: str):
        super().__init__("web-knowledge-extraction", shared_secret)
        self.insights: Dict[str, ResearchInsight] = {}
        self.entity_patterns = {
            'methodology': r'\b(machine learning|neural network|deep learning|algorithm|model|AI|artificial intelligence)\b',
            'metric': r'\b(accuracy|precision|recall|performance|improvement|efficiency)\b',
            'domain': r'\b(climate|weather|quantum|cryptography|security|prediction|forecasting)\b',
            'institution': r'\b(NIST|Nature|Science|IEEE|MIT|Stanford|Google|Microsoft)\b'
        }
        
        self._register_handlers()
    
    def _register_handlers(self):
        """Register message handlers for this service."""
        self.register_handler('extract_web_insights', self.handle_extract_web_insights)
        self.register_handler('analyze_source_credibility', self.handle_analyze_credibility)
        self.register_handler('identify_research_trends', self.handle_identify_trends)
    
    async def handle_extract_web_insights(self, message: A2AMessage):
        """Handle insight extraction from web search results."""
        search_results = message.payload.get('search_results', [])
        
        insights = []
        for result_data in search_results:
            result_insights = self._extract_insights_from_result(result_data)
            insights.extend(result_insights)
        
        print(f"[{self.service_name}] Extracted {len(insights)} insights from {len(search_results)} web sources")
        
        for insight in insights:
            self.insights[insight.id] = insight
    
    def _extract_insights_from_result(self, result_data: Dict[str, Any]) -> List[ResearchInsight]:
        """Extract insights from a single search result."""
        content = result_data.get('snippet', '') + ' ' + result_data.get('title', '')
        insights = []
        
        # Extract methodology insights
        methods = re.findall(self.entity_patterns['methodology'], content, re.IGNORECASE)
        if methods:
            insight = ResearchInsight(
                id=str(uuid.uuid4()),
                content=f"Methodologies found: {', '.join(set(methods))}",
                confidence=0.8,
                source_urls=[result_data.get('url', '')],
                insight_type='methodology',
                extracted_at=datetime.utcnow().isoformat()
            )
            insights.append(insight)
        
        # Extract domain insights
        domains = re.findall(self.entity_patterns['domain'], content, re.IGNORECASE)
        if domains:
            insight = ResearchInsight(
                id=str(uuid.uuid4()),
                content=f"Research domains: {', '.join(set(domains))}",
                confidence=0.9,
                source_urls=[result_data.get('url', '')],
                insight_type='domain',
                extracted_at=datetime.utcnow().isoformat()
            )
            insights.append(insight)
        
        # Extract institutional insights
        institutions = re.findall(self.entity_patterns['institution'], content, re.IGNORECASE)
        if institutions:
            insight = ResearchInsight(
                id=str(uuid.uuid4()),
                content=f"Key institutions: {', '.join(set(institutions))}",
                confidence=0.85,
                source_urls=[result_data.get('url', '')],
                insight_type='institution',
                extracted_at=datetime.utcnow().isoformat()
            )
            insights.append(insight)
        
        return insights
    
    async def handle_analyze_credibility(self, message: A2AMessage):
        """Handle source credibility analysis."""
        search_results = message.payload.get('search_results', [])
        
        credibility_analysis = self._analyze_source_credibility(search_results)
        print(f"[{self.service_name}] Analyzed credibility of {len(search_results)} sources")
        print(f"[{self.service_name}] High credibility sources: {credibility_analysis['high_credibility_count']}")
    
    def _analyze_source_credibility(self, search_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze the credibility of search result sources."""
        high_credibility_sources = {
            'nature.com', 'science.org', 'ieee.org', 'acm.org', 'nist.gov',
            'arxiv.org', 'pubmed.ncbi.nlm.nih.gov', 'scholar.google.com'
        }
        
        analysis = {
            'total_sources': len(search_results),
            'high_credibility_count': 0,
            'medium_credibility_count': 0,
            'low_credibility_count': 0,
            'source_breakdown': defaultdict(int)
        }
        
        for result in search_results:
            url = result.get('url', '')
            domain = self._extract_domain(url)
            
            analysis['source_breakdown'][domain] += 1
            
            if any(trusted in url for trusted in high_credibility_sources):
                analysis['high_credibility_count'] += 1
            elif domain.endswith('.edu') or domain.endswith('.gov'):
                analysis['medium_credibility_count'] += 1
            else:
                analysis['low_credibility_count'] += 1
        
        return analysis
    
    async def handle_identify_trends(self, message: A2AMessage):
        """Handle research trend identification from web sources."""
        search_results = message.payload.get('search_results', [])
        
        trends = self._identify_web_trends(search_results)
        print(f"[{self.service_name}] Identified {len(trends)} trends from web research")
    
    def _identify_web_trends(self, search_results: List[Dict[str, Any]]) -> List[str]:
        """Identify trends from web search results."""
        trend_keywords = defaultdict(int)
        
        for result in search_results:
            content = (result.get('snippet', '') + ' ' + result.get('title', '')).lower()
            
            # Count trend indicators
            trend_words = ['emerging', 'novel', 'breakthrough', 'innovative', 'recent', 'latest', 'new']
            for word in trend_words:
                if word in content:
                    trend_keywords[word] += 1
        
        return list(trend_keywords.keys())
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        if not url:
            return ''
        parts = url.split('/')
        return parts[2] if len(parts) > 2 else url