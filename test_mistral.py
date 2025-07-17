#!/usr/bin/env python3
"""Simple test script to verify Mistral integration is working."""

import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from a2a_research.distributed_client import DistributedA2AClient

async def test_mistral_integration():
    """Test the full research workflow with Mistral."""
    client = DistributedA2AClient()
    
    # Discover services
    print("🔍 Discovering services...")
    if not await client.discover_services():
        print("❌ Failed to discover services")
        return False
    
    print(f"✅ Found {len(client.services)} services")
    
    # Test search
    print("\n🔍 Testing search...")
    try:
        search_results = await client.perform_distributed_search("quantum computing advances", max_results=3)
        print(f"✅ Search returned {len(search_results)} results")
        
        if search_results:
            print(f"First result: {search_results[0].get('title', 'No title')}")
    except Exception as e:
        print(f"❌ Search failed: {e}")
        return False
    
    # Test knowledge extraction
    print("\n🧠 Testing knowledge extraction...")
    try:
        insights = await client.extract_insights(search_results[:2])  # Use fewer results
        print(f"✅ Knowledge extraction returned {insights.get('total_insights', 0)} insights")
        
        if insights.get('insights'):
            print(f"First insight: {insights['insights'][0].get('content', 'No content')[:100]}...")
    except Exception as e:
        print(f"❌ Knowledge extraction failed: {e}")
        return False
    
    # Test research session
    print("\n📊 Testing research session...")
    try:
        session_id = await client.start_research_session("quantum computing advances")
        print(f"✅ Started session: {session_id}")
        
        # Aggregate results
        await client.aggregate_results(session_id, search_results)
        print("✅ Aggregated results")
        
        # Generate report
        report = await client.generate_report(session_id)
        print(f"✅ Generated report with {len(report)} sections")
        
        if report.get('executive_summary'):
            print(f"Executive Summary: {report['executive_summary'][:100]}...")
            
    except Exception as e:
        print(f"❌ Research session failed: {e}")
        return False
    
    print("\n🎉 All tests passed! Mistral integration is working correctly.")
    return True

if __name__ == "__main__":
    asyncio.run(test_mistral_integration())