"""
Debug test to see what GPT-5 is actually returning
"""

import asyncio
import os
from pathlib import Path

# Load environment variables
env_file = Path(__file__).parent / '.env'
if env_file.exists():
    with open(env_file, 'r') as f:
        for line in f:
            if '=' in line and not line.strip().startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

from openai import AsyncOpenAI

async def debug_gpt5_response():
    """Debug what GPT-5 is actually returning."""
    
    api_key = os.getenv('LLM_API_KEY') or os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ No API key found")
        return
    
    client = AsyncOpenAI(api_key=api_key)
    
    # Simple test prompt
    system_prompt = """You are a business analyst. Extract insights from this meeting transcript.

Return JSON array format:
[
  {
    "insight_type": "action_item",
    "title": "Brief title",
    "description": "Detailed description",
    "severity": "high",
    "confidence_score": 0.9
  }
]"""
    
    user_prompt = """Meeting: Q4 Status
Mike: We have a critical security vulnerability. Will cost $50,000 penalty if we miss deadline.
Sarah: Schedule emergency CTO meeting.
ACTION: Mike to provide security report by COB."""
    
    print("🧠 Testing GPT-5 response format...")
    
    try:
        response = await client.chat.completions.create(
            model="gpt-5",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_completion_tokens=1000
        )
        
        response_text = response.choices[0].message.content
        
        print("📄 GPT-5 Raw Response:")
        print("=" * 50)
        print(response_text)
        print("=" * 50)
        
        # Try to parse as JSON
        import json
        try:
            parsed = json.loads(response_text)
            print("✅ JSON parsing successful!")
            print(f"📊 Found {len(parsed)} insights")
            for i, insight in enumerate(parsed, 1):
                print(f"  {i}. {insight.get('insight_type', 'unknown')}: {insight.get('title', 'no title')}")
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing failed: {e}")
            print("🔍 Checking for JSON in markdown...")
            
            import re
            json_match = re.search(r'```(?:json)?\s*(\[.*?\])\s*```', response_text, re.DOTALL)
            if json_match:
                try:
                    parsed = json.loads(json_match.group(1))
                    print("✅ Found JSON in markdown!")
                    print(f"📊 Found {len(parsed)} insights")
                except:
                    print("❌ Even markdown JSON failed")
            else:
                print("❌ No JSON found in markdown either")
        
    except Exception as e:
        print(f"❌ API call failed: {e}")

if __name__ == "__main__":
    asyncio.run(debug_gpt5_response())
