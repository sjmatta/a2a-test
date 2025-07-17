#!/usr/bin/env python3
"""
Fallback Knowledge Extraction Service - Works without Mistral if needed.
"""

import uuid
import json
from typing import List, Dict, Any
from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import uvicorn
import httpx

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from a2a_research.models import ResearchInsight
from a2a_research.servers.auth import create_auth_dependency, A2AAuth


# Pydantic models for API
class ExtractionRequest(BaseModel):
    search_results: List[Dict[str, Any]]


class InsightResponse(BaseModel):
    insights: List[Dict[str, Any]]
    total_insights: int


class KnowledgeExtractionServer:
    """Knowledge Extraction Service with Mistral + fallback."""
    
    def __init__(self, port: int = 8002, shared_secret: str = "demo-secret"):
        self.port = port
        self.shared_secret = shared_secret
        self.auth = A2AAuth(shared_secret)
        self.insights: Dict[str, ResearchInsight] = {}
        
        # Create FastAPI app
        self.app = FastAPI(
            title="A2A Knowledge Extraction Service",
            description="Knowledge extraction with Mistral and fallback",
            version="1.0.0"
        )
        
        # Create auth dependency
        self.verify_auth = create_auth_dependency(self.shared_secret)
        
        # Setup routes
        self._setup_routes()
        
        print(f"[knowledge-server] ✅ Ready with Mistral + fallback")
    
    def _setup_routes(self):
        """Setup FastAPI routes."""
        
        @self.app.get("/health")
        async def health_check():
            return {"status": "healthy", "service": "knowledge-extraction"}
        
        @self.app.post("/extract", response_model=InsightResponse)
        async def extract_insights(
            request: ExtractionRequest,
            authenticated_service: str = Depends(self.verify_auth)
        ):
            """Extract insights from search results."""
            print(f"[knowledge-server] Processing {len(request.search_results)} results")
            
            all_insights = []
            for result_data in request.search_results:
                # Try Mistral first, fallback to simple extraction
                try:
                    insights = await self._extract_with_mistral(result_data)
                    print(f"[knowledge-server] ✅ Mistral extracted {len(insights)} insights")
                except Exception as e:
                    print(f"[knowledge-server] ⚠️ Mistral failed: {e}, using fallback")
                    insights = self._extract_with_fallback(result_data)
                    print(f"[knowledge-server] ✅ Fallback extracted {len(insights)} insights")
                
                all_insights.extend(insights)
            
            # Store insights
            for insight in all_insights:
                self.insights[insight.id] = insight
            
            print(f"[knowledge-server] ✅ Total: {len(all_insights)} insights")
            
            return InsightResponse(
                insights=[self._insight_to_dict(insight) for insight in all_insights],
                total_insights=len(all_insights)
            )
    
    async def _extract_with_mistral(self, result_data: Dict[str, Any]) -> List[ResearchInsight]:
        """Extract insights using Mistral."""
        content = result_data.get('snippet', '') + ' ' + result_data.get('title', '')
        url = result_data.get('url', '')
        
        prompt = f"""Extract 5-8 insights from this content:

Content: "{content}"

Return JSON array: [{{"content": "insight description", "insight_type": "overview", "confidence": 0.9}}]

Categories: overview, methodology, domain, findings, significance"""

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                "http://127.0.0.1:1234/v1/chat/completions",
                json={
                    "model": "mistralai/mistral-small-3.2",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                    "max_tokens": 800
                }
            )
            
            result = response.json()
            response_text = result['choices'][0]['message']['content'].strip()
        
        # Extract JSON
        if '```json' in response_text:
            start = response_text.find('```json') + 7
            end = response_text.find('```', start)
            json_text = response_text[start:end].strip()
        else:
            start = response_text.find('[')
            end = response_text.rfind(']') + 1
            json_text = response_text[start:end]
        
        llm_insights = json.loads(json_text)
        
        # Convert to ResearchInsight objects
        insights = []
        for insight_data in llm_insights:
            insight = ResearchInsight(
                id=str(uuid.uuid4()),
                content=insight_data.get('content', ''),
                confidence=insight_data.get('confidence', 0.9),
                source_urls=[url],
                insight_type=insight_data.get('insight_type', 'general'),
                extracted_at=datetime.utcnow().isoformat()
            )
            insights.append(insight)
        
        return insights
    
    def _extract_with_fallback(self, result_data: Dict[str, Any]) -> List[ResearchInsight]:
        """Simple fallback extraction without LLM."""
        content = result_data.get('snippet', '') + ' ' + result_data.get('title', '')
        url = result_data.get('url', '')
        title = result_data.get('title', '')
        
        insights = []
        
        # Create basic insights from title and content
        if title:
            insights.append(ResearchInsight(
                id=str(uuid.uuid4()),
                content=f"Source discusses: {title}",
                confidence=0.8,
                source_urls=[url],
                insight_type='overview',
                extracted_at=datetime.utcnow().isoformat()
            ))
        
        if content:
            # Extract key phrases
            words = content.lower().split()
            key_terms = [word for word in words if len(word) > 5 and word.isalpha()]
            
            if key_terms:
                insights.append(ResearchInsight(
                    id=str(uuid.uuid4()),
                    content=f"Key terms mentioned: {', '.join(key_terms[:5])}",
                    confidence=0.7,
                    source_urls=[url],
                    insight_type='domain',
                    extracted_at=datetime.utcnow().isoformat()
                ))
            
            # Basic content analysis
            if 'news' in content.lower() or 'latest' in content.lower():
                insights.append(ResearchInsight(
                    id=str(uuid.uuid4()),
                    content="Source contains recent news or updates",
                    confidence=0.8,
                    source_urls=[url],
                    insight_type='significance',
                    extracted_at=datetime.utcnow().isoformat()
                ))
        
        return insights
    
    def _insight_to_dict(self, insight: ResearchInsight) -> Dict[str, Any]:
        """Convert ResearchInsight to dictionary."""
        return {
            "id": insight.id,
            "content": insight.content,
            "confidence": insight.confidence,
            "source_urls": insight.source_urls,
            "insight_type": insight.insight_type,
            "extracted_at": insight.extracted_at
        }
    
    def run(self):
        """Run the knowledge extraction server."""
        print(f"Starting Knowledge Extraction Server on port {self.port}")
        uvicorn.run(self.app, host="127.0.0.1", port=self.port)


if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8002
    server = KnowledgeExtractionServer(port=port)
    server.run()