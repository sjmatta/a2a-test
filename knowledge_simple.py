#!/usr/bin/env python3
"""Clean, simple knowledge extraction using only Mistral."""

import asyncio
import json
import httpx

async def test_clean_extraction():
    """Test clean Mistral extraction."""
    
    # Test data
    content = "Quantum computing uses quantum bits (qubits) to perform parallel computations that could revolutionize cryptography and optimization problems."
    
    prompt = f"""Extract 5-10 insights from this content in JSON format:

Content: "{content}"

Return JSON array:
[{{"content": "insight description", "insight_type": "overview", "confidence": 0.95}}]

Categories: overview, methodology, domain, findings, significance"""

    print("🧠 Testing clean Mistral extraction...")
    
    async with httpx.AsyncClient() as client:
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
        content = result['choices'][0]['message']['content']
        
        # Simple JSON extraction
        if '```json' in content:
            start = content.find('```json') + 7
            end = content.find('```', start)
            json_text = content[start:end].strip()
        else:
            start = content.find('[')
            end = content.rfind(']') + 1
            json_text = content[start:end]
        
        insights = json.loads(json_text)
        
        print(f"✅ Extracted {len(insights)} insights:")
        for insight in insights:
            print(f"  • {insight['content'][:60]}... ({insight['insight_type']})")
        
        return insights

if __name__ == "__main__":
    asyncio.run(test_clean_extraction())