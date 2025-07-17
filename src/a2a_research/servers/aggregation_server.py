#!/usr/bin/env python3
"""
Research Aggregation Service Server - Handles research session management via HTTP API.
"""

import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from collections import defaultdict

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import uvicorn

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from a2a_research.servers.auth import create_auth_dependency, A2AAuth


# Pydantic models for API
class SessionRequest(BaseModel):
    topic: str
    session_id: Optional[str] = None


class AggregateRequest(BaseModel):
    session_id: str
    results: List[Dict[str, Any]]


class ReportRequest(BaseModel):
    session_id: str


class SessionResponse(BaseModel):
    session_id: str
    topic: str
    started_at: str


class ReportResponse(BaseModel):
    report: Dict[str, Any]


class ResearchAggregationServer:
    """Research Aggregation Service Server."""
    
    def __init__(self, port: int = 8003, shared_secret: str = "demo-secret"):
        self.port = port
        self.shared_secret = shared_secret
        self.auth = A2AAuth(shared_secret)
        self.research_sessions: Dict[str, Dict[str, Any]] = {}
        
        # Create FastAPI app
        self.app = FastAPI(
            title="A2A Research Aggregation Service",
            description="Distributed research aggregation service for A2A research platform",
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
            return {"status": "healthy", "service": "research-aggregation"}
        
        @self.app.post("/session", response_model=SessionResponse)
        async def start_session(
            request: SessionRequest,
            authenticated_service: str = Depends(self.verify_auth)
        ):
            """Start a new research session."""
            session_id = request.session_id or str(uuid.uuid4())
            
            self.research_sessions[session_id] = {
                'id': session_id,
                'topic': request.topic,
                'started_at': datetime.utcnow().isoformat(),
                'search_results': [],
                'insights': [],
                'queries': [],
                'sources_analyzed': 0
            }
            
            print(f"[aggregation-server] Started research session from {authenticated_service}: {request.topic} ({session_id})")
            
            return SessionResponse(
                session_id=session_id,
                topic=request.topic,
                started_at=self.research_sessions[session_id]['started_at']
            )
        
        @self.app.post("/aggregate")
        async def aggregate_results(
            request: AggregateRequest,
            authenticated_service: str = Depends(self.verify_auth)
        ):
            """Aggregate research results for a session."""
            if request.session_id not in self.research_sessions:
                raise HTTPException(status_code=404, detail="Session not found")
            
            session = self.research_sessions[request.session_id]
            session['search_results'].extend(request.results)
            session['sources_analyzed'] += len(request.results)
            
            print(f"[aggregation-server] Aggregated {len(request.results)} results from {authenticated_service} for session {request.session_id}")
            
            return {"status": "aggregated", "total_results": len(session['search_results'])}
        
        @self.app.post("/report", response_model=ReportResponse)
        async def generate_report(
            request: ReportRequest,
            authenticated_service: str = Depends(self.verify_auth)
        ):
            """Generate research report for a session."""
            if request.session_id not in self.research_sessions:
                raise HTTPException(status_code=404, detail="Session not found")
            
            session = self.research_sessions[request.session_id]
            report = self._generate_web_research_report(session)
            
            print(f"[aggregation-server] Generated report from {authenticated_service} for: {session['topic']}")
            print(f"[aggregation-server] Report summary: {session['sources_analyzed']} web sources analyzed")
            
            return ReportResponse(report=report)
        
        @self.app.get("/sessions")
        async def list_sessions(authenticated_service: str = Depends(self.verify_auth)):
            """List all research sessions."""
            return {
                "sessions": [
                    {
                        "session_id": session_id,
                        "topic": session_data["topic"],
                        "started_at": session_data["started_at"],
                        "sources_analyzed": session_data["sources_analyzed"]
                    }
                    for session_id, session_data in self.research_sessions.items()
                ]
            }
        
        @self.app.get("/sessions/{session_id}")
        async def get_session(
            session_id: str,
            authenticated_service: str = Depends(self.verify_auth)
        ):
            """Get details for a specific session."""
            if session_id not in self.research_sessions:
                raise HTTPException(status_code=404, detail="Session not found")
            
            return self.research_sessions[session_id]
    
    def _generate_web_research_report(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a comprehensive web research report using LLM analysis."""
        search_results = session.get('search_results', [])
        insights = session.get('insights', [])
        
        # Use LLM to generate comprehensive research report
        try:
            # Prepare content for LLM analysis
            sources_summary = []
            for result in search_results:
                sources_summary.append({
                    'title': result.get('title', 'No title'),
                    'url': result.get('url', ''),
                    'snippet': result.get('snippet', '')[:200] + '...' if len(result.get('snippet', '')) > 200 else result.get('snippet', ''),
                    'source': result.get('source', '')
                })
            
            insights_summary = []
            for insight in insights:
                insights_summary.append({
                    'content': insight.get('content', ''),
                    'type': insight.get('insight_type', ''),
                    'confidence': insight.get('confidence', 0.0)
                })
            
            prompt = f"""You are a research report generator. Create a comprehensive, detailed research report based on the following information.

TOPIC: {session['topic']}
SOURCES ANALYZED: {len(search_results)}
INSIGHTS EXTRACTED: {len(insights)}

SOURCES:
{chr(10).join([f"• {s['title']} ({s['source']}): {s['snippet']}" for s in sources_summary[:10]])}

INSIGHTS:
{chr(10).join([f"• {i['content']}" for i in insights_summary[:15]])}

Generate a comprehensive research report in JSON format with the following structure:
{{
  "executive_summary": "2-3 paragraph comprehensive overview of the topic",
  "key_findings": ["finding1", "finding2", "finding3", "finding4", "finding5"],
  "detailed_analysis": "4-5 paragraph deep analysis covering multiple aspects",
  "methodology_notes": "Description of research approach and sources",
  "significance_assessment": "Analysis of importance and impact",
  "related_topics": ["topic1", "topic2", "topic3"],
  "source_quality_assessment": "Evaluation of source reliability and diversity",
  "research_gaps": ["gap1", "gap2", "gap3"],
  "recommendations": ["recommendation1", "recommendation2", "recommendation3"],
  "conclusion": "2-3 paragraph conclusion summarizing insights and implications"
}}

Make the report comprehensive, detailed, and academically rigorous. Each section should be substantial and informative."""

            import httpx
            import json
            
            # Use synchronous call since we're in a sync method
            import requests
            response = requests.post(
                "http://127.0.0.1:1234/v1/chat/completions",
                json={
                    "model": "mistralai/mistral-small-3.2",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                    "max_tokens": 2000
                },
                timeout=60.0
            )
            
            if response.status_code == 200:
                llm_response = response.json()
                response_text = llm_response['choices'][0]['message']['content'].strip()
                
                # Parse JSON response
                if '```json' in response_text:
                    json_start = response_text.find('```json') + 7
                    json_end = response_text.find('```', json_start)
                    json_text = response_text[json_start:json_end].strip()
                elif response_text.startswith('{') and response_text.endswith('}'):
                    json_text = response_text
                else:
                    start_idx = response_text.find('{')
                    end_idx = response_text.rfind('}') + 1
                    if start_idx != -1 and end_idx > start_idx:
                        json_text = response_text[start_idx:end_idx]
                    else:
                        raise Exception("No valid JSON found in LLM response")
                
                llm_report = json.loads(json_text)
                
                # Combine LLM report with basic statistics
                report = {
                    'session_id': session['id'],
                    'topic': session['topic'],
                    'generated_at': datetime.utcnow().isoformat(),
                    'total_sources': len(search_results),
                    'unique_domains': len(set(self._extract_domain(r.get('url', '')) for r in search_results)),
                    'average_relevance': self._calculate_avg_relevance(search_results),
                    'session_duration': self._calculate_duration(session['started_at']),
                    'total_insights': len(insights),
                    **llm_report  # Add all LLM-generated content
                }
                
                print(f"[aggregation-server] Generated comprehensive LLM report with {len(llm_report)} sections")
                return report
                
        except Exception as e:
            print(f"[aggregation-server] Failed to generate LLM report: {e}")
            
        # Fallback to basic report
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
            'research_coverage': self._assess_coverage(search_results),
            'session_duration': self._calculate_duration(session['started_at']),
            'total_insights': len(insights),
            'executive_summary': f"Basic research report on {session['topic']} analyzing {len(search_results)} sources.",
            'key_findings': ['Analysis completed', 'Sources reviewed', 'Insights extracted']
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
            
            if any(term in url or term in source for term in ['nature', 'science', 'ieee', 'arxiv', 'pubmed', 'scholar']):
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
    
    def _calculate_duration(self, started_at: str) -> str:
        """Calculate session duration."""
        try:
            start_time = datetime.fromisoformat(started_at.replace('Z', '+00:00'))
            current_time = datetime.utcnow()
            duration = current_time - start_time.replace(tzinfo=None)
            
            total_seconds = int(duration.total_seconds())
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            
            return f"{minutes}m {seconds}s"
        except:
            return "Unknown"
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        if not url:
            return ''
        parts = url.split('/')
        return parts[2] if len(parts) > 2 else url
    
    def run(self):
        """Run the research aggregation server."""
        print(f"Starting Research Aggregation Server on port {self.port}")
        uvicorn.run(self.app, host="127.0.0.1", port=self.port)


if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8003
    server = ResearchAggregationServer(port=port)
    server.run()