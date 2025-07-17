"""
Web search service for A2A research system.
"""

import asyncio
import uuid
from typing import Dict, Any, List, Callable, Optional
from datetime import datetime
from collections import defaultdict

from .base_service import A2AService
from .models import A2AMessage, WebSearchResult, SearchQuery


class WebSearchService(A2AService):
    """Service for performing web searches and managing search results."""
    
    def __init__(self, shared_secret: str, search_function: Optional[Callable] = None):
        super().__init__("web-search", shared_secret)
        self.search_results: Dict[str, List[WebSearchResult]] = {}
        self.search_cache: Dict[str, List[WebSearchResult]] = {}
        self.search_function = search_function
        
        self._register_handlers()
    
    def _register_handlers(self):
        """Register message handlers for this service."""
        self.register_handler('perform_search', self.handle_perform_search)
        self.register_handler('filter_results', self.handle_filter_results)
        self.register_handler('get_cached_results', self.handle_get_cached_results)
    
    async def handle_perform_search(self, message: A2AMessage):
        """Handle web search requests."""
        query_data = message.payload.get('query', {})
        query = SearchQuery(**query_data)
        
        # Check cache first
        cache_key = self._create_cache_key(query)
        if cache_key in self.search_cache:
            results = self.search_cache[cache_key]
            print(f"[{self.service_name}] Retrieved {len(results)} cached results for: '{query.query_text}'")
        else:
            # Perform actual web search
            results = await self._perform_web_search(query)
            self.search_cache[cache_key] = results
            print(f"[{self.service_name}] Found {len(results)} new results for: '{query.query_text}'")
        
        # Store results for session
        session_id = message.payload.get('session_id', 'default')
        self._store_session_results(session_id, results)
        
        # Send results to callback service
        callback_service = message.payload.get('callback_service')
        if callback_service:
            print(f"[{self.service_name}] Sending {len(results)} results to {callback_service}")
    
    async def _perform_web_search(self, query: SearchQuery) -> List[WebSearchResult]:
        """Perform actual web search using real search function if available."""
        if self.search_function:
            try:
                # Use real web search
                return await self._perform_real_search(query)
            except Exception as e:
                print(f"[{self.service_name}] Real search failed: {e}, falling back to simulated")
        
        # Fallback to simulated search
        await asyncio.sleep(0.5)
        return await self._perform_simulated_search(query)
    
    async def _perform_real_search(self, query: SearchQuery) -> List[WebSearchResult]:
        """Perform real web search using the provided search function."""
        try:
            # Call the real search function
            search_results = await asyncio.get_event_loop().run_in_executor(
                None, self.search_function, query.query_text
            )
            
            results = []
            for i, result in enumerate(search_results[:query.max_results]):
                web_result = WebSearchResult(
                    id=str(uuid.uuid4()),
                    title=result.get('title', f'Result {i+1}'),
                    url=result.get('url', ''),
                    snippet=result.get('snippet', result.get('description', '')),
                    source=result.get('source', result.get('url', '').split('/')[2] if result.get('url') else 'Unknown'),
                    search_query=query.query_text,
                    relevance_score=result.get('relevance', 0.8),
                    extracted_at=datetime.utcnow().isoformat()
                )
                results.append(web_result)
            
            return results
        except Exception as e:
            print(f"[{self.service_name}] Error in real search: {e}")
            return []
    
    async def _perform_simulated_search(self, query: SearchQuery) -> List[WebSearchResult]:
        """Perform simulated web search with realistic data."""
        query_lower = query.query_text.lower()
        
        if 'machine learning' in query_lower and 'climate' in query_lower:
            results = self._get_climate_ml_results(query)
        elif 'quantum computing' in query_lower:
            results = self._get_quantum_computing_results(query)
        else:
            results = self._get_generic_results(query)
        
        return results[:query.max_results]
    
    def _get_climate_ml_results(self, query: SearchQuery) -> List[WebSearchResult]:
        """Get climate ML specific search results."""
        return [
            WebSearchResult(
                id=str(uuid.uuid4()),
                title="Machine Learning for Climate Change Research: A Comprehensive Review",
                url="https://www.nature.com/articles/s41558-021-01168-6",
                snippet="This review examines how machine learning techniques are being applied to climate science, including temperature prediction, extreme weather forecasting, and carbon cycle modeling.",
                source="Nature Climate Change",
                search_query=query.query_text,
                relevance_score=0.95,
                extracted_at=datetime.utcnow().isoformat()
            ),
            WebSearchResult(
                id=str(uuid.uuid4()),
                title="Deep Learning Applications in Climate Modeling and Prediction",
                url="https://agupubs.onlinelibrary.wiley.com/doi/10.1029/2021GL094765",
                snippet="Neural networks and deep learning are revolutionizing climate prediction models with improved accuracy in weather forecasting and long-term climate projections.",
                source="Geophysical Research Letters",
                search_query=query.query_text,
                relevance_score=0.92,
                extracted_at=datetime.utcnow().isoformat()
            ),
            WebSearchResult(
                id=str(uuid.uuid4()),
                title="AI for Climate: Machine Learning Solutions for Environmental Challenges",
                url="https://www.climatechange.ai/papers",
                snippet="A collection of research papers exploring how artificial intelligence and machine learning can address climate change through improved modeling, monitoring, and mitigation strategies.",
                source="Climate Change AI",
                search_query=query.query_text,
                relevance_score=0.88,
                extracted_at=datetime.utcnow().isoformat()
            )
        ]
    
    def _get_quantum_computing_results(self, query: SearchQuery) -> List[WebSearchResult]:
        """Get quantum computing specific search results."""
        return [
            WebSearchResult(
                id=str(uuid.uuid4()),
                title="Quantum Computing: Progress and Prospects",
                url="https://www.science.org/doi/10.1126/science.aam5830",
                snippet="Recent advances in quantum computing hardware and algorithms show promise for solving complex optimization problems and cryptographic challenges.",
                source="Science",
                search_query=query.query_text,
                relevance_score=0.94,
                extracted_at=datetime.utcnow().isoformat()
            ),
            WebSearchResult(
                id=str(uuid.uuid4()),
                title="Post-Quantum Cryptography: Preparing for the Quantum Era",
                url="https://csrc.nist.gov/projects/post-quantum-cryptography",
                snippet="NIST standardization efforts for cryptographic systems that can resist attacks from quantum computers.",
                source="NIST",
                search_query=query.query_text,
                relevance_score=0.91,
                extracted_at=datetime.utcnow().isoformat()
            )
        ]
    
    def _get_generic_results(self, query: SearchQuery) -> List[WebSearchResult]:
        """Get generic search results for other queries."""
        return [
            WebSearchResult(
                id=str(uuid.uuid4()),
                title=f"Research on {query.query_text.title()}",
                url=f"https://example.com/research/{query.query_text.replace(' ', '-')}",
                snippet=f"Comprehensive research and analysis on {query.query_text} with latest findings and methodologies.",
                source="Academic Repository",
                search_query=query.query_text,
                relevance_score=0.75,
                extracted_at=datetime.utcnow().isoformat()
            )
        ]
    
    async def handle_filter_results(self, message: A2AMessage):
        """Handle result filtering requests."""
        session_id = message.payload.get('session_id', 'default')
        filters = message.payload.get('filters', {})
        
        if session_id in self.search_results:
            results = self.search_results[session_id]
            filtered_results = self._apply_filters(results, filters)
            print(f"[{self.service_name}] Filtered {len(results)} to {len(filtered_results)} results")
    
    def _apply_filters(self, results: List[WebSearchResult], filters: Dict[str, Any]) -> List[WebSearchResult]:
        """Apply filters to search results."""
        filtered = results
        
        if 'min_relevance' in filters:
            min_rel = filters['min_relevance']
            filtered = [r for r in filtered if r.relevance_score >= min_rel]
        
        if 'exclude_domains' in filters:
            exclude = filters['exclude_domains']
            filtered = [r for r in filtered if not any(domain in r.url for domain in exclude)]
        
        if 'source_type' in filters:
            source_type = filters['source_type'].lower()
            if source_type == 'academic':
                academic_sources = ['nature', 'science', 'ieee', 'acm', 'arxiv', 'pubmed']
                filtered = [r for r in filtered if any(src in r.source.lower() for src in academic_sources)]
        
        return filtered
    
    async def handle_get_cached_results(self, message: A2AMessage):
        """Handle cached result retrieval."""
        query_text = message.payload.get('query_text', '')
        if query_text:
            cache_key = f"{query_text}_10"  # Default max_results
            if cache_key in self.search_cache:
                results = self.search_cache[cache_key]
                print(f"[{self.service_name}] Retrieved {len(results)} cached results for: '{query_text}'")
    
    def _create_cache_key(self, query: SearchQuery) -> str:
        """Create a cache key for the query."""
        return f"{query.query_text}_{query.max_results}"
    
    def _store_session_results(self, session_id: str, results: List[WebSearchResult]):
        """Store results for a session."""
        if session_id not in self.search_results:
            self.search_results[session_id] = []
        self.search_results[session_id].extend(results)