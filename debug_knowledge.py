#!/usr/bin/env python3
"""Debug knowledge extraction service."""

import asyncio
import sys
import os
import json
import traceback
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from a2a_research.servers.auth import A2AAuth

async def test_knowledge_extraction():
    """Test knowledge extraction with proper auth."""
    import httpx
    
    # Create proper auth headers
    auth = A2AAuth("demo-secret")
    headers = auth.create_auth_headers("test-client", "")
    headers["Content-Type"] = "application/json"
    
    # Test data
    test_data = {
        "search_results": [
            {
                "title": "Quantum Computing Advances",
                "url": "https://example.com/quantum",
                "snippet": "Quantum computing uses quantum bits (qubits) to perform parallel computations that could revolutionize cryptography and optimization problems.",
                "source": "example.com"
            }
        ]
    }
    
    print("🧠 Testing knowledge extraction with Mistral...")
    print(f"Headers: {headers}")
    print(f"Payload: {json.dumps(test_data, indent=2)}")
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "http://127.0.0.1:8002/extract",
                json=test_data,
                headers=headers
            )
            
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Success! Got {data.get('total_insights', 0)} insights")
                for insight in data.get('insights', [])[:3]:
                    print(f"  • {insight.get('content', 'No content')[:100]}...")
            else:
                print(f"❌ Failed: {response.status_code} - {response.text}")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_knowledge_extraction())