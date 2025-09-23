"""
Comprehensive debug test for GPT-5 API issues
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

async def comprehensive_debug():
    """Comprehensive debug of GPT-5 API."""
    
    api_key = os.getenv('LLM_API_KEY') or os.getenv('OPENAI_API_KEY')
    model_choice = os.getenv('LLM_CHOICE', 'gpt-5')
    
    print(f"🔧 Configuration:")
    print(f"   Model: {model_choice}")
    print(f"   API Key: {'✅ Found' if api_key else '❌ Missing'}")
    
    if not api_key:
        print("❌ No API key found")
        return
    
    client = AsyncOpenAI(api_key=api_key)
    
    # Test 1: List available models
    print("\n📋 Step 1: Listing available models...")
    try:
        models = await client.models.list()
        model_names = [model.id for model in models.data]
        print(f"   ✅ Found {len(model_names)} models")
        
        # Check if our model is available
        if model_choice in model_names:
            print(f"   ✅ {model_choice} is available")
        else:
            print(f"   ❌ {model_choice} NOT found in available models")
            print("   🔍 Similar models found:")
            similar = [m for m in model_names if 'gpt' in m.lower()]
            for model in similar[:10]:
                print(f"      - {model}")
            
            # Try with a known working model
            print(f"\n🔄 Switching to gpt-4o-mini for testing...")
            model_choice = "gpt-4o-mini"
    
    except Exception as e:
        print(f"   ❌ Failed to list models: {e}")
        return
    
    # Test 2: Simple completion test
    print(f"\n🧠 Step 2: Testing simple completion with {model_choice}...")
    try:
        simple_response = await client.chat.completions.create(
            model=model_choice,
            messages=[
                {"role": "user", "content": "Say 'Hello, this is a test!' and nothing else."}
            ],
            max_completion_tokens=50
        )
        
        simple_text = simple_response.choices[0].message.content
        print(f"   📄 Simple response: '{simple_text}'")
        
        if simple_text and simple_text.strip():
            print("   ✅ Basic completion working")
        else:
            print("   ❌ Empty response from simple test")
            return
            
    except Exception as e:
        print(f"   ❌ Simple completion failed: {e}")
        return
    
    # Test 3: JSON format test
    print(f"\n📋 Step 3: Testing JSON format response...")
    try:
        json_response = await client.chat.completions.create(
            model=model_choice,
            messages=[
                {"role": "system", "content": "You must respond only with valid JSON. No other text."},
                {"role": "user", "content": "Return this JSON: {\"test\": \"success\", \"number\": 42}"}
            ],
            max_completion_tokens=100
        )
        
        json_text = json_response.choices[0].message.content
        print(f"   📄 JSON response: '{json_text}'")
        
        # Try to parse it
        import json
        try:
            parsed = json.loads(json_text)
            print(f"   ✅ JSON parsing successful: {parsed}")
        except json.JSONDecodeError as e:
            print(f"   ❌ JSON parsing failed: {e}")
            
    except Exception as e:
        print(f"   ❌ JSON test failed: {e}")
    
    # Test 4: Business insights test with working model
    print(f"\n💼 Step 4: Testing business insights extraction...")
    try:
        insights_response = await client.chat.completions.create(
            model=model_choice,
            messages=[
                {"role": "system", "content": """Extract business insights and return as JSON array.
                
Format:
[
  {
    "type": "action_item",
    "title": "Brief title",
    "description": "Description",
    "severity": "high"
  }
]

Return ONLY the JSON array, no other text."""},
                {"role": "user", "content": """Meeting notes:
Mike: We have a critical security vulnerability that will cost $50,000 penalty if we miss the January deadline.
Sarah: Schedule emergency meeting with CTO tomorrow.
Action: Mike to provide security report by end of day."""}
            ],
            max_completion_tokens=500
        )
        
        insights_text = insights_response.choices[0].message.content
        print(f"   📄 Insights response length: {len(insights_text)} chars")
        print(f"   📄 First 200 chars: '{insights_text[:200]}...'")
        
        # Try to parse
        import json
        try:
            parsed_insights = json.loads(insights_text)
            print(f"   ✅ Insights parsing successful!")
            print(f"   📊 Found {len(parsed_insights)} insights")
            for i, insight in enumerate(parsed_insights, 1):
                print(f"      {i}. {insight.get('type', 'unknown')}: {insight.get('title', 'no title')}")
        except json.JSONDecodeError as e:
            print(f"   ❌ Insights JSON parsing failed: {e}")
            print("   🔍 Looking for patterns in response...")
            
            # Look for common patterns
            if '[' in insights_text and ']' in insights_text:
                print("   📋 Found array brackets - might be malformed JSON")
            if '{' in insights_text and '}' in insights_text:
                print("   📋 Found object brackets - might be embedded JSON")
            if 'action' in insights_text.lower():
                print("   📋 Found 'action' keyword - content is relevant")
            
    except Exception as e:
        print(f"   ❌ Business insights test failed: {e}")
    
    print(f"\n🎯 Summary:")
    print(f"   Model tested: {model_choice}")
    print(f"   Next steps: Use working model for insights extraction")

if __name__ == "__main__":
    asyncio.run(comprehensive_debug())
