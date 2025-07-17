#!/usr/bin/env python3
"""
Simple Knowledge Extraction Service - Uses only Mistral, no fallbacks.
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
    """Simple Knowledge Extraction Service using only Mistral."""
    
    def __init__(self, port: int = 8002, shared_secret: str = "demo-secret"):
        self.port = port
        self.shared_secret = shared_secret
        self.auth = A2AAuth(shared_secret)
        self.insights: Dict[str, ResearchInsight] = {}
        
        # Create FastAPI app
        self.app = FastAPI(
            title="A2A Knowledge Extraction Service",
            description="Simple knowledge extraction using Mistral",
            version="1.0.0"
        )
        
        # Create auth dependency
        self.verify_auth = create_auth_dependency(self.shared_secret)
        
        # Setup routes
        self._setup_routes()
        
        print(f"[knowledge-server] ✅ Using Mistral: mistralai/mistral-small-3.2")
    
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
            """Extract insights from search results using Mistral."""
            print(f"[knowledge-server] Processing {len(request.search_results)} results with Mistral")
            
            all_insights = []
            for result_data in request.search_results:
                insights = await self._extract_with_mistral(result_data)
                all_insights.extend(insights)
            
            # Store insights
            for insight in all_insights:
                self.insights[insight.id] = insight
            
            print(f"[knowledge-server] ✅ Extracted {len(all_insights)} insights with Mistral")
            
            return InsightResponse(
                insights=[self._insight_to_dict(insight) for insight in all_insights],
                total_insights=len(all_insights)
            )
    
    async def _extract_with_mistral(self, result_data: Dict[str, Any]) -> List[ResearchInsight]:
        """Extract insights using Mistral."""
        content = result_data.get('snippet', '') + ' ' + result_data.get('title', '')
        url = result_data.get('url', '')
        
        prompt = f"""Extract 8-12 insights from this content:

Content: "{content}"
Source: {url}

Return JSON array with insights in these categories:
- overview: main concepts and purpose
- methodology: techniques and approaches  
- domain: research fields and applications
- findings: key results and discoveries
- significance: impact and importance

Format: [{{"content": "detailed insight description", "insight_type": "overview", "confidence": 0.95}}]"""

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "http://127.0.0.1:1234/v1/chat/completions",
                json={
                    "model": "mistralai/mistral-small-3.2",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                    "max_tokens": 1500
                }
            )
            
            result = response.json()
            response_text = result['choices'][0]['message']['content'].strip()
        
        # Extract JSON from Mistral response
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
        
        print(f"[knowledge-server] ✅ Mistral extracted {len(insights)} insights")
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
        print(f"Starting Simple Knowledge Extraction Server on port {self.port}")
        uvicorn.run(self.app, host="127.0.0.1", port=self.port)


if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8002
    server = KnowledgeExtractionServer(port=port)
    server.run()