#!/usr/bin/env python3
"""
Knowledge Extraction Service Server - Handles insight extraction via HTTP API.
"""

import re
import uuid
from typing import List, Dict, Any
from datetime import datetime
from collections import defaultdict
import asyncio
import json

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


class CredibilityRequest(BaseModel):
    search_results: List[Dict[str, Any]]


class InsightResponse(BaseModel):
    insights: List[Dict[str, Any]]
    total_insights: int


class CredibilityResponse(BaseModel):
    analysis: Dict[str, Any]


class KnowledgeExtractionServer:
    """Knowledge Extraction Service Server."""
    
    def __init__(self, port: int = 8002, shared_secret: str = "demo-secret"):
        self.port = port
        self.shared_secret = shared_secret
        self.auth = A2AAuth(shared_secret)
        self.insights: Dict[str, ResearchInsight] = {}
        
        # Initialize LM Studio connection
        self.setup_lm_studio()
        
        # Entity extraction patterns (fallback)
        self.entity_patterns = {
            'methodology': r'\b(machine learning|neural network|deep learning|algorithm|model|AI|artificial intelligence)\b',
            'metric': r'\b(accuracy|precision|recall|performance|improvement|efficiency)\b',
            'domain': r'\b(climate|weather|quantum|cryptography|security|prediction|forecasting)\b',
            'institution': r'\b(NIST|Nature|Science|IEEE|MIT|Stanford|Google|Microsoft|arXiv)\b'
        }
    
    def setup_lm_studio(self):
        """Setup LM Studio connection for local Gemma3."""
        try:
            # Default LM Studio endpoint (user can override with env var)
            self.lm_studio_url = os.getenv('LM_STUDIO_URL', 'http://127.0.0.1:1234')
            
            # Test connection to LM Studio
            import requests
            response = requests.get(f"{self.lm_studio_url}/v1/models", timeout=2)
            if response.status_code == 200:
                models = response.json()
                if models.get('data'):
                    # Find a suitable LLM (avoid embedding models)
                    available_models = [m['id'] for m in models['data']]
                    
                    # Prefer Gemma, then Llama, then others, but skip embedding models
                    for model_id in available_models:
                        if 'embedding' not in model_id.lower():
                            if any(name in model_id.lower() for name in ['gemma', 'llama', 'phi', 'deepseek']):
                                self.model_name = model_id
                                break
                    else:
                        # Fallback to first non-embedding model
                        self.model_name = next((m for m in available_models if 'embedding' not in m.lower()), available_models[0])
                    
                    self.use_llm = True
                    print(f"[knowledge-server] ✅ LM Studio connected with LLM: {self.model_name}")
                    print(f"[knowledge-server] Available models: {', '.join(available_models)}")
                else:
                    raise Exception("No models available in LM Studio")
            else:
                raise Exception(f"LM Studio not responding: {response.status_code}")
        except Exception as e:
            print(f"[knowledge-server] ⚠️  LM Studio setup failed: {e}, using regex fallback")
            print(f"[knowledge-server] ⚠️  Make sure LM Studio is running on {self.lm_studio_url}")
            self.use_llm = False
        
        # Create FastAPI app
        self.app = FastAPI(
            title="A2A Knowledge Extraction Service",
            description="Distributed knowledge extraction service for A2A research platform",
            version="1.0.0"
        )
        
        # Create auth dependency
        self.verify_auth = create_auth_dependency(self.shared_secret)
        
        # Setup routes
        self._setup_routes()
    
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
            print(f"[knowledge-server] Insight extraction request from {authenticated_service}")
            
            insights = []
            for result_data in request.search_results:
                result_insights = await self._extract_insights_from_result(result_data)
                insights.extend(result_insights)
            
            # Store insights
            for insight in insights:
                self.insights[insight.id] = insight
            
            print(f"[knowledge-server] Extracted {len(insights)} insights from {len(request.search_results)} sources")
            
            return InsightResponse(
                insights=[self._insight_to_dict(insight) for insight in insights],
                total_insights=len(insights)
            )
        
        @self.app.post("/credibility", response_model=CredibilityResponse)
        async def analyze_credibility(
            request: CredibilityRequest,
            authenticated_service: str = Depends(self.verify_auth)
        ):
            """Analyze source credibility."""
            print(f"[knowledge-server] Credibility analysis request from {authenticated_service}")
            
            if self.use_llm:
                analysis = await self._analyze_credibility_with_llm(request.search_results)
            else:
                analysis = self._analyze_source_credibility(request.search_results)
            
            print(f"[knowledge-server] Analyzed {len(request.search_results)} sources")
            print(f"[knowledge-server] High credibility: {analysis['high_credibility_count']}")
            
            return CredibilityResponse(analysis=analysis)
        
        @self.app.get("/insights/stats")
        async def insights_stats(authenticated_service: str = Depends(self.verify_auth)):
            """Get insights statistics."""
            insight_types = defaultdict(int)
            for insight in self.insights.values():
                insight_types[insight.insight_type] += 1
            
            return {
                "total_insights": len(self.insights),
                "insights_by_type": dict(insight_types)
            }
    
    async def _extract_insights_from_result(self, result_data: Dict[str, Any]) -> List[ResearchInsight]:
        """Extract insights from a single search result using LLM or regex fallback."""
        if self.use_llm:
            return await self._extract_insights_with_llm(result_data)
        else:
            return self._extract_insights_with_regex(result_data)
    
    async def _extract_insights_with_llm(self, result_data: Dict[str, Any]) -> List[ResearchInsight]:
        """Extract insights using local LM Studio with Gemma3."""
        try:
            content = result_data.get('snippet', '') + ' ' + result_data.get('title', '')
            url = result_data.get('url', '')
            
            prompt = f"""You are a comprehensive research analyst. Perform deep analysis of the following content and extract extensive structured insights.

Content: "{content}"
Source: {url}

Provide comprehensive analysis in these categories:
1. **overview** - Main topic, purpose, core concepts
2. **methodology** - Research methods, algorithms, techniques, approaches
3. **domain** - Research fields, application areas, disciplines
4. **findings** - Key discoveries, results, conclusions, outcomes
5. **institution** - Organizations, authors, affiliations, companies
6. **significance** - Impact, importance, implications, relevance
7. **context** - Historical background, related work, connections
8. **details** - Technical specifications, features, characteristics
9. **timeline** - Dates, chronology, development history
10. **relationships** - Connections to other topics, dependencies

For each insight, provide:
- Detailed content description (2-3 sentences)
- High confidence scores for clear insights
- Multiple insights per category when possible

Return ONLY a JSON array with this exact format:
[
  {{"content": "detailed insight description with context and significance", "insight_type": "overview", "confidence": 0.95}},
  {{"content": "another comprehensive insight with background and implications", "insight_type": "methodology", "confidence": 0.88}}
]

Extract 15-25 insights total. Be thorough and comprehensive."""

            # Call LM Studio API
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.lm_studio_url}/v1/chat/completions",
                    json={
                        "model": self.model_name,
                        "messages": [
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.3,
                        "max_tokens": 1000
                    },
                    timeout=30.0
                )
                
                if response.status_code != 200:
                    raise Exception(f"LM Studio API error: {response.status_code}")
                
                llm_response = response.json()
                response_text = llm_response['choices'][0]['message']['content'].strip()
            
            # Parse LLM response
            # Extract JSON from response (handle markdown code blocks)
            if '```json' in response_text:
                json_start = response_text.find('```json') + 7
                json_end = response_text.find('```', json_start)
                json_text = response_text[json_start:json_end].strip()
            elif response_text.startswith('[') and response_text.endswith(']'):
                json_text = response_text
            else:
                # Try to find JSON array in response
                start_idx = response_text.find('[')
                end_idx = response_text.rfind(']') + 1
                if start_idx != -1 and end_idx > start_idx:
                    json_text = response_text[start_idx:end_idx]
                else:
                    print(f"[knowledge-server] LM Studio response not in expected format: {response_text[:100]}...")
                    return []
            
            llm_insights = json.loads(json_text)
            
            # Convert to ResearchInsight objects
            insights = []
            for llm_insight in llm_insights:
                insight = ResearchInsight(
                    id=str(uuid.uuid4()),
                    content=llm_insight.get('content', ''),
                    confidence=llm_insight.get('confidence', 0.7),
                    source_urls=[url],
                    insight_type=llm_insight.get('insight_type', 'general'),
                    extracted_at=datetime.utcnow().isoformat()
                )
                insights.append(insight)
            
            print(f"[knowledge-server] ✅ LM Studio extracted {len(insights)} insights from: {url[:50]}...")
            return insights
            
        except Exception as e:
            print(f"[knowledge-server] ❌ LM Studio extraction failed: {e}, falling back to regex")
            return self._extract_insights_with_regex(result_data)
    
    def _extract_insights_with_regex(self, result_data: Dict[str, Any]) -> List[ResearchInsight]:
        """Extract insights using regex patterns (fallback)."""
        content = result_data.get('snippet', '') + ' ' + result_data.get('title', '')
        insights = []
        url = result_data.get('url', '')
        
        # Extract methodology insights
        methods = re.findall(self.entity_patterns['methodology'], content, re.IGNORECASE)
        if methods:
            insight = ResearchInsight(
                id=str(uuid.uuid4()),
                content=f"Methodologies found: {', '.join(set(methods))}",
                confidence=0.8,
                source_urls=[url],
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
                source_urls=[url],
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
                source_urls=[url],
                insight_type='institution',
                extracted_at=datetime.utcnow().isoformat()
            )
            insights.append(insight)
        
        return insights
    
    async def _analyze_credibility_with_llm(self, search_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze source credibility using LM Studio."""
        try:
            # Prepare source list for LLM analysis
            sources_text = ""
            for i, result in enumerate(search_results):
                title = result.get('title', 'No title')
                url = result.get('url', '')
                source = result.get('source', '')
                sources_text += f"{i+1}. Title: {title}\n   URL: {url}\n   Source: {source}\n\n"
            
            prompt = f"""You are a research credibility analyst. Analyze these {len(search_results)} sources and rate their credibility.

Sources:
{sources_text}

For each source, consider:
- Domain authority (.edu, .gov, academic journals, known institutions)
- Publication type (peer-reviewed, news, blog, etc.)
- Author credentials and institutional affiliation
- Content quality indicators

Return ONLY this JSON format:
{{
  "total_sources": {len(search_results)},
  "high_credibility_count": <number>,
  "medium_credibility_count": <number>, 
  "low_credibility_count": <number>,
  "source_breakdown": {{"domain1": count1, "domain2": count2}},
  "credibility_reasons": ["reason1", "reason2"]
}}

High credibility: Academic journals, .edu/.gov, established institutions
Medium credibility: News sites, .org, professional organizations  
Low credibility: Blogs, social media, unverified sources"""

            # Call LM Studio API
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.lm_studio_url}/v1/chat/completions",
                    json={
                        "model": self.model_name,
                        "messages": [
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.1,
                        "max_tokens": 800
                    },
                    timeout=30.0
                )
                
                if response.status_code != 200:
                    raise Exception(f"LM Studio API error: {response.status_code}")
                
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
                # Try to find JSON object in response
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}') + 1
                if start_idx != -1 and end_idx > start_idx:
                    json_text = response_text[start_idx:end_idx]
                else:
                    raise Exception("No valid JSON found in LLM response")
            
            analysis = json.loads(json_text)
            print(f"[knowledge-server] ✅ LM Studio credibility analysis completed")
            return analysis
            
        except Exception as e:
            print(f"[knowledge-server] ❌ LLM credibility analysis failed: {e}, falling back to rule-based")
            return self._analyze_source_credibility(search_results)
    
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
        
        # Convert defaultdict to regular dict for JSON serialization
        analysis['source_breakdown'] = dict(analysis['source_breakdown'])
        
        return analysis
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        if not url:
            return ''
        parts = url.split('/')
        return parts[2] if len(parts) > 2 else url
    
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