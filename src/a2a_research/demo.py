"""
Web research demo orchestration.
"""

import asyncio

from .search_service import WebSearchService
from .knowledge_service import WebKnowledgeExtractionService
from .aggregation_service import WebResearchAggregationService


async def run_web_research_demo():
    """Run the web-based research A2A communication demonstration."""
    print("=== Web Research A2A Communication Demo ===\n")
    
    # Shared secret for service authentication
    shared_secret = "web-research-demo-secret-key-67890"
    
    # Create web research services
    web_search = WebSearchService(shared_secret)
    web_knowledge = WebKnowledgeExtractionService(shared_secret)
    web_research_agg = WebResearchAggregationService(shared_secret)
    
    # Start message processing tasks
    tasks = [
        asyncio.create_task(web_search.process_messages()),
        asyncio.create_task(web_knowledge.process_messages()),
        asyncio.create_task(web_research_agg.process_messages())
    ]
    
    await asyncio.sleep(0.1)
    
    try:
        await _run_demo_workflow(web_search, web_knowledge, web_research_agg)
    finally:
        # Cancel tasks
        for task in tasks:
            task.cancel()


async def _run_demo_workflow(web_search, web_knowledge, web_research_agg):
    """Run the demo workflow steps."""
    
    print("1. Starting web research session on 'Machine Learning for Climate Science'...")
    await web_research_agg.send_message(web_research_agg, {
        'type': 'start_web_research_session',
        'session': {
            'id': 'web-session-001',
            'topic': 'Machine Learning for Climate Science'
        }
    })
    
    await asyncio.sleep(0.5)
    
    print("\n2. Performing web search for climate ML research...")
    await web_search.send_message(web_search, {
        'type': 'perform_search',
        'query': {
            'id': 'web-query-001',
            'query_text': 'machine learning climate change research',
            'max_results': 3
        },
        'session_id': 'web-session-001',
        'callback_service': 'web-research-aggregation'
    })
    
    await asyncio.sleep(1.0)  # Allow time for simulated web search
    
    print("\n3. Performing additional search on quantum computing...")
    await web_search.send_message(web_search, {
        'type': 'perform_search',
        'query': {
            'id': 'web-query-002',
            'query_text': 'quantum computing cryptography',
            'max_results': 2
        },
        'session_id': 'web-session-001',
        'callback_service': 'web-research-aggregation'
    })
    
    await asyncio.sleep(1.0)
    
    print("\n4. Extracting insights from web search results...")
    sample_results = _get_sample_results()
    
    await web_knowledge.send_message(web_knowledge, {
        'type': 'extract_web_insights',
        'search_results': sample_results
    })
    
    await asyncio.sleep(0.5)
    
    print("\n5. Analyzing source credibility...")
    await web_knowledge.send_message(web_knowledge, {
        'type': 'analyze_source_credibility',
        'search_results': sample_results
    })
    
    await asyncio.sleep(0.5)
    
    print("\n6. Identifying research trends from web sources...")
    await web_knowledge.send_message(web_knowledge, {
        'type': 'identify_research_trends',
        'search_results': sample_results
    })
    
    await asyncio.sleep(0.5)
    
    print("\n7. Aggregating web research results...")
    await web_research_agg.send_message(web_research_agg, {
        'type': 'aggregate_web_results',
        'session_id': 'web-session-001',
        'results': sample_results
    })
    
    await asyncio.sleep(0.3)
    
    print("\n8. Generating comprehensive web research report...")
    await web_research_agg.send_message(web_research_agg, {
        'type': 'generate_web_report',
        'session_id': 'web-session-001'
    })
    
    await asyncio.sleep(1)
    
    print("\n=== Web Research Demo Complete ===")
    print("Demonstrated: Web search integration, real-time source analysis,")
    print("credibility assessment, insight extraction, and comprehensive reporting.")


def _get_sample_results():
    """Get sample search results for demonstration."""
    return [
        {
            'title': 'Machine Learning for Climate Change Research',
            'snippet': 'Deep learning and neural networks are revolutionizing climate prediction models with improved accuracy.',
            'url': 'https://www.nature.com/articles/climate-ml-2024',
            'source': 'Nature Climate Change'
        },
        {
            'title': 'Quantum Computing Applications in Cryptography',
            'snippet': 'NIST standardization efforts for post-quantum cryptography algorithms to resist quantum attacks.',
            'url': 'https://csrc.nist.gov/quantum-crypto',
            'source': 'NIST'
        }
    ]