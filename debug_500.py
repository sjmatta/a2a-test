#!/usr/bin/env python3
"""Debug the 500 error in knowledge extraction."""

import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from a2a_research.distributed_client import DistributedA2AClient

async def debug_knowledge_extraction():
    """Debug the knowledge extraction 500 error."""
    
    client = DistributedA2AClient()
    
    # Test data similar to Final Fantasy VI search
    test_results = [
        {
            "title": "Final Fantasy VI Coverage - GamesRadar+",
            "url": "https://www.gamesradar.com/games/final-fantasy/final-fantasy-vi/",
            "snippet": "The latest Final Fantasy VI breaking news, comment, reviews and features from the experts at GamesRadar+",
            "source": "www.gamesradar.com",
            "relevance_score": 0.9
        }
    ]
    
    print("🔍 Discovering services...")
    if not await client.discover_services():
        print("❌ Failed to discover services")
        return
    
    print("🧠 Testing knowledge extraction...")
    try:
        result = await client.extract_insights(test_results)
        print(f"✅ Success! Got {result.get('total_insights', 0)} insights")
        for insight in result.get('insights', [])[:3]:
            print(f"  • {insight.get('content', '')[:80]}...")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_knowledge_extraction())