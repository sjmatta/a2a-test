#!/usr/bin/env python3
"""Test knowledge server directly to debug 500 error."""

import asyncio
import json
import httpx
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from a2a_research.servers.auth import A2AAuth

async def test_knowledge_server():
    """Test the knowledge server directly."""
    
    # Create proper auth
    auth = A2AAuth("demo-secret")
    headers = auth.create_auth_headers("test-client", "")
    headers["Content-Type"] = "application/json"
    
    test_payload = {
        "search_results": [
            {
                "title": "Final Fantasy VI Coverage - GamesRadar+",
                "url": "https://www.gamesradar.com/games/final-fantasy/final-fantasy-vi/",
                "snippet": "The latest Final Fantasy VI breaking news, comment, reviews and features from the experts at GamesRadar+",
                "source": "www.gamesradar.com"
            }
        ]
    }
    
    print("🧠 Testing knowledge server directly...")
    print(f"URL: http://127.0.0.1:8002/extract")
    print(f"Headers: {headers}")
    print(f"Payload: {json.dumps(test_payload, indent=2)}")
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "http://127.0.0.1:8002/extract",
                json=test_payload,
                headers=headers
            )
            
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Success! Got {data.get('total_insights', 0)} insights")
                for insight in data.get('insights', []):
                    print(f"  • {insight.get('content', '')[:100]}...")
            else:
                print(f"❌ Failed: {response.status_code}")
                print(f"Error: {response.text}")
                
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_knowledge_server())