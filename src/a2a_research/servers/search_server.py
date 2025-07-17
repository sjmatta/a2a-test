#!/usr/bin/env python3
"""
Web Search Service Server - Handles search requests via HTTP API.
"""

import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio

from fastapi import FastAPI, HTTPException, Depends, Body
from pydantic import BaseModel
import uvicorn
from duckduckgo_search import DDGS
import requests
from bs4 import BeautifulSoup

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from a2a_research.models import SearchQuery, WebSearchResult
from a2a_research.servers.auth import create_auth_dependency, A2AAuth


# Pydantic models for API
class SearchRequest(BaseModel):
    query_text: str
    max_results: int = 10
    session_id: Optional[str] = None
    follow_up_queries: Optional[List[str]] = None
    comprehensive: bool = False


class SearchResponse(BaseModel):
    results: List[Dict[str, Any]]
    query: str
    total_results: int


class WebSearchServer:
    """Web Search Service Server."""
    
    def __init__(self, port: int = 8001, shared_secret: str = "demo-secret"):
        self.port = port
        self.shared_secret = shared_secret
        self.auth = A2AAuth(shared_secret)
        
        # Create FastAPI app
        self.app = FastAPI(
            title="A2A Web Search Service",
            description="Distributed web search service for A2A research platform",
            version="1.0.0"
        )
        
        # Create auth dependency
        self.verify_auth = create_auth_dependency(shared_secret)
        
        # Setup routes
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup FastAPI routes."""
        
        @self.app.get("/health")
        async def health_check():
            return {"status": "healthy", "service": "web-search"}
        
        @self.app.post("/search", response_model=SearchResponse)
        async def perform_search(
            request: SearchRequest,
            authenticated_service: str = Depends(self.verify_auth)
        ):
            """Perform web search and return results."""
            print(f"[web-search-server] Search request from {authenticated_service}: '{request.query_text}'")
            
            all_results = []
            
            # Primary search
            search_query = SearchQuery(
                id=str(uuid.uuid4()),
                query_text=request.query_text,
                max_results=request.max_results
            )
            
            primary_results = await self._perform_search(search_query)
            all_results.extend(primary_results)
            
            # If comprehensive search requested, perform follow-up searches
            if request.comprehensive:
                follow_up_queries = request.follow_up_queries or await self._generate_follow_up_queries(request.query_text)
                
                for follow_up_query in follow_up_queries[:3]:  # Limit to 3 follow-up queries
                    print(f"[web-search-server] Follow-up search: '{follow_up_query}'")
                    
                    follow_up_search = SearchQuery(
                        id=str(uuid.uuid4()),
                        query_text=follow_up_query,
                        max_results=max(5, request.max_results // 2)  # Fewer results per follow-up
                    )
                    
                    follow_up_results = await self._perform_search(follow_up_search)
                    all_results.extend(follow_up_results)
            
            # Remove duplicates based on URL
            unique_results = []
            seen_urls = set()
            for result in all_results:
                if result.url not in seen_urls:
                    unique_results.append(result)
                    seen_urls.add(result.url)
            
            print(f"[web-search-server] Found {len(unique_results)} unique results from {len(all_results)} total searches")
            
            return SearchResponse(
                results=[self._result_to_dict(r) for r in unique_results],
                query=request.query_text,
                total_results=len(unique_results)
            )
        
    
    async def _perform_search(self, query: SearchQuery) -> List[WebSearchResult]:
        """Perform actual web search using DuckDuckGo."""
        try:
            print(f"[web-search-server] Performing real DuckDuckGo search for: '{query.query_text}'")
            
            # Use DuckDuckGo search in a thread to avoid blocking
            loop = asyncio.get_event_loop()
            ddg_results = await loop.run_in_executor(
                None, 
                self._ddg_search, 
                query.query_text, 
                query.max_results
            )
            
            results = []
            for i, ddg_result in enumerate(ddg_results):
                print(f"[web-search-server] DEBUG: Processing result {i+1}: {ddg_result.get('title', 'No title')[:50]}...")
                
                # Extract content from the page
                content = await self._extract_page_content(ddg_result.get('href', ''))
                
                result = WebSearchResult(
                    id=str(uuid.uuid4()),
                    title=ddg_result.get('title', 'No title'),
                    url=ddg_result.get('href', ''),
                    snippet=ddg_result.get('body', content[:200] + '...' if content else 'No snippet available'),
                    source=self._extract_domain(ddg_result.get('href', '')),
                    search_query=query.query_text,
                    relevance_score=max(0.9 - (i * 0.1), 0.1),  # Decreasing relevance
                    extracted_at=datetime.utcnow().isoformat()
                )
                results.append(result)
                print(f"[web-search-server] DEBUG: Added result: {result.title[:50]}... from {result.source}")
            
            print(f"[web-search-server] Successfully found {len(results)} real search results")
            return results
            
        except Exception as e:
            print(f"[web-search-server] Search error: {e}")
            # Fallback to minimal results if search fails
            return [
                WebSearchResult(
                    id=str(uuid.uuid4()),
                    title=f"Search results for: {query.query_text}",
                    url="https://duckduckgo.com/?q=" + query.query_text.replace(' ', '+'),
                    snippet=f"Real search temporarily unavailable. Query: {query.query_text}",
                    source="DuckDuckGo",
                    search_query=query.query_text,
                    relevance_score=0.5,
                    extracted_at=datetime.utcnow().isoformat()
                )
            ]
    
    def _ddg_search(self, query_text: str, max_results: int) -> List[Dict[str, Any]]:
        """Perform DuckDuckGo search (synchronous)."""
        print(f"[web-search-server] DEBUG: DuckDuckGo search for: '{query_text}' (max: {max_results})")
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query_text, max_results=max_results))
                print(f"[web-search-server] DEBUG: DDG returned {len(results)} results")
                for i, result in enumerate(results[:2]):  # Log first 2 results
                    print(f"[web-search-server] DEBUG: Result {i+1}: {result.get('title', 'No title')[:50]}...")
                    print(f"[web-search-server] DEBUG: URL {i+1}: {result.get('href', 'No URL')[:50]}...")
                return results
        except Exception as e:
            print(f"[web-search-server] ERROR: DuckDuckGo search failed: {e}")
            return []
    
    async def _extract_page_content(self, url: str) -> str:
        """Extract text content from a web page."""
        try:
            if not url or not url.startswith(('http://', 'https://')):
                return ""
            
            # Use a thread for the blocking request
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.get(url, timeout=5, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
            )
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()
                
                # Get text content
                text = soup.get_text()
                
                # Clean up whitespace
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = ' '.join(chunk for chunk in chunks if chunk)
                
                return text[:1000]  # Limit to first 1000 characters
                
        except Exception as e:
            print(f"[web-search-server] Content extraction error for {url}: {e}")
            return ""
        
        return ""
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        try:
            if not url:
                return "Unknown"
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc or "Unknown"
        except:
            return "Unknown"
    
    async def _generate_follow_up_queries(self, original_query: str) -> List[str]:
        """Generate follow-up queries using LLM for comprehensive research."""
        try:
            # Use LM Studio to generate intelligent follow-up queries
            prompt = f"""You are a research assistant. Given the original search query, generate 5 diverse follow-up search queries that would provide comprehensive coverage of the topic.

Original query: "{original_query}"

IMPORTANT: Keep the main subject/entity from the original query intact in each follow-up query. Don't break it apart.

Generate search queries that explore different aspects like:
- Historical context and background
- Technical details and analysis
- Impact and significance
- Related concepts and connections
- Current developments and future

Return ONLY a JSON array of strings:
["query1", "query2", "query3", "query4", "query5"]

Example for "Final Fantasy VI":
["Final Fantasy VI development history", "Final Fantasy VI characters storyline", "Final Fantasy VI impact on RPG genre", "Final Fantasy VI ports remasters", "Final Fantasy VI soundtrack composer"]

Make each query specific and preserve the exact original subject name."""

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "http://127.0.0.1:1234/v1/chat/completions",
                    json={
                        "model": "meta-llama-3.1-8b-instruct",
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.7,
                        "max_tokens": 300
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    llm_response = response.json()
                    response_text = llm_response['choices'][0]['message']['content'].strip()
                    
                    # Parse JSON response
                    if '```json' in response_text:
                        json_start = response_text.find('```json') + 7
                        json_end = response_text.find('```', json_start)
                        json_text = response_text[json_start:json_end].strip()
                    elif response_text.startswith('[') and response_text.endswith(']'):
                        json_text = response_text
                    else:
                        start_idx = response_text.find('[')
                        end_idx = response_text.rfind(']') + 1
                        if start_idx != -1 and end_idx > start_idx:
                            json_text = response_text[start_idx:end_idx]
                        else:
                            raise Exception("No valid JSON found in LLM response")
                    
                    import json
                    follow_up_queries = json.loads(json_text)
                    print(f"[web-search-server] LLM generated {len(follow_up_queries)} follow-up queries")
                    return follow_up_queries
                    
        except Exception as e:
            print(f"[web-search-server] Failed to generate LLM follow-up queries: {e}")
            
        # Simple fallback if LLM fails
        return [
            f"{original_query} background",
            f"{original_query} analysis", 
            f"{original_query} details"
        ]
    
    def _result_to_dict(self, result: WebSearchResult) -> Dict[str, Any]:
        """Convert WebSearchResult to dictionary."""
        return {
            "id": result.id,
            "title": result.title,
            "url": result.url,
            "snippet": result.snippet,
            "source": result.source,
            "relevance_score": result.relevance_score,
            "extracted_at": result.extracted_at
        }
    
    def run(self):
        """Run the search server."""
        print(f"Starting Web Search Server on port {self.port}")
        uvicorn.run(self.app, host="127.0.0.1", port=self.port)


if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8001
    server = WebSearchServer(port=port)
    server.run()