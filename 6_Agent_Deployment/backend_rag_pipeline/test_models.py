"""
Test multiple models to find the best working one for insights
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

async def test_models():
    """Test multiple models to find the best working one."""
    
    api_key = os.getenv('LLM_API_KEY') or os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ No API key found")
        return
    
    client = AsyncOpenAI(api_key=api_key)
    
    # Models to test in order of preference
    models_to_test = [
        "gpt-5-mini",
        "gpt-4o",
        "gpt-4o-mini", 
        "gpt-4-turbo",
        "gpt-4",
        "gpt-3.5-turbo"
    ]
    
    test_prompt = """Extract business insights from this meeting:
Mike: Critical security vulnerability found. $50,000 penalty if we miss January deadline.
Sarah: Schedule emergency CTO meeting tomorrow.
Action: Mike to provide security report by COB.

Return JSON array:
[{"type": "risk", "title": "Security Vulnerability", "severity": "critical"}]"""
    
    working_models = []
    
    for model in models_to_test:
        print(f"\n🧠 Testing {model}...")
        
        try:
            response = await client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": test_prompt}
                ],
                max_completion_tokens=500,
                temperature=0.1
            )
            
            response_text = response.choices[0].message.content
            
            if response_text and response_text.strip():
                print(f"   ✅ {model} responded ({len(response_text)} chars)")
                print(f"   📄 Preview: '{response_text[:100]}...'")
                
                # Try to parse JSON
                import json
                try:
                    parsed = json.loads(response_text)
                    print(f"   ✅ Valid JSON! Found {len(parsed)} insights")
                    working_models.append((model, "json_working"))
                except json.JSONDecodeError:
                    # Check if it contains insight content
                    if any(word in response_text.lower() for word in ['security', 'vulnerability', 'risk', 'action']):
                        print(f"   ⚠️  Contains insights but not JSON format")
                        working_models.append((model, "content_good"))
                    else:
                        print(f"   ❌ Response doesn't contain expected insights")
            else:
                print(f"   ❌ {model} returned empty response")
                
        except Exception as e:
            print(f"   ❌ {model} failed: {e}")
    
    print(f"\n🎯 Results Summary:")
    if working_models:
        print("   ✅ Working models found:")
        for model, status in working_models:
            print(f"      - {model}: {status}")
        
        # Recommend best model
        best_model = working_models[0][0]
        print(f"\n🚀 Recommended model: {best_model}")
        
        # Update .env file
        print(f"📝 Updating .env file to use {best_model}...")
        env_path = Path(__file__).parent / '.env'
        if env_path.exists():
            with open(env_path, 'r') as f:
                content = f.read()
            
            # Replace LLM_CHOICE line
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('LLM_CHOICE='):
                    lines[i] = f'LLM_CHOICE={best_model}'
                    break
            
            with open(env_path, 'w') as f:
                f.write('\n'.join(lines))
            
            print(f"   ✅ Updated LLM_CHOICE to {best_model}")
        
    else:
        print("   ❌ No working models found")

if __name__ == "__main__":
    asyncio.run(test_models())
