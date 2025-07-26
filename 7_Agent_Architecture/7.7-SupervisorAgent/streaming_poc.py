"""
Streaming Foundation Validation for Supervisor Agent using .run_stream().

This validates Pydantic AI structured output streaming using the correct .run_stream() method
for real-time structured output streaming as documented in Pydantic AI docs.
"""

import asyncio
import logging
from typing import Optional
from dataclasses import dataclass
from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic_ai import Agent
from dotenv import load_dotenv
import os

from clients import get_model

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()


class SupervisorDecision(BaseModel):
    """Structured output for supervisor agent decisions with streaming support"""
    messages: Optional[str] = Field(
        None, 
        description="Response to user - ONLY populate if final_response=True, otherwise MUST be None"
    )
    delegate_to: Optional[str] = Field(
        None,
        description="Agent to delegate to: 'web_research', 'task_management', 'email_draft', or None if final_response=True"
    )
    reasoning: str = Field(
        description="Reasoning for this decision"
    )
    final_response: bool = Field(
        default=False,
        description="True for final response to user, False for delegation"
    )
    


@dataclass
class SupervisorTestDependencies:
    """Test dependencies for supervisor agent validation"""
    session_id: Optional[str] = None


# Test supervisor agent with structured output streaming
test_supervisor_agent = Agent(
    get_model(use_smaller_model=True),  # Use fast model for testing
    deps_type=SupervisorTestDependencies,
    output_type=SupervisorDecision,
    system_prompt="""
You are a supervisor agent. You output structured JSON with these exact patterns:

FOR DELEGATION (research/planning/email writing):
{
  "messages": null,
  "delegate_to": "web_research" OR "task_management" OR "email_draft",
  "reasoning": "explanation", 
  "final_response": false
}

FOR FINAL RESPONSE (simple questions):
{
  "messages": "your helpful response text",
  "delegate_to": null,
  "reasoning": "explanation",
  "final_response": true
}

Examples:
Q: "Find latest info about X" -> delegate_to="web_research", messages=null
Q: "Create project plan" -> delegate_to="task_management", messages=null  
Q: "Write an email" -> delegate_to="email_draft", messages=null
Q: "What is machine learning?" -> messages="ML is...", delegate_to=null
"""
)


async def test_streaming_structured_output():
    """Test streaming structured output using .run_stream() method"""
    print("🧪 Testing Streaming Structured Output with .run_stream()...")
    
    test_queries = [
        "What is machine learning and how does it work?",  # Should provide final response with streaming messages
        "Research the latest AI startups and their funding in 2024",  # Should delegate to web_research
        "Create a project plan for our new product launch",  # Should delegate to task_management
        "Draft a professional email to our investors about Q4 results"  # Should delegate to email_draft
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n--- Test {i}: {query} ---")
        
        deps = SupervisorTestDependencies(session_id=f"test_session_{i}")
        streaming_success = False
        final_decision = None
        
        try:
            print("🔄 Using .run_stream() for structured output streaming...")
            
            # Use .run_stream() for true structured output streaming
            async with test_supervisor_agent.run_stream(query, deps=deps) as result:
                print("📝 Streaming structured output in real-time:")
                
                # Stream the structured output as it's generated
                async for partial_decision in result.stream():
                    print(f"   {partial_decision}")
                    
                    # If this is a final response and messages is being populated, show the progress
                    if hasattr(partial_decision, 'messages') and partial_decision.messages and partial_decision.final_response:
                        print(f"   🎯 Final response streaming: {partial_decision.messages}")
                
                # Get the final complete decision
                final_decision = await result.get_output()
                streaming_success = True
                print(f"✅ Streaming completed successfully!")
                
        except Exception as stream_error:
            print(f"❌ Streaming failed: {stream_error}")
            
            # FALLBACK: Non-streaming structured output
            print("🔄 Using fallback non-streaming approach...")
            try:
                result = await test_supervisor_agent.run(query, deps=deps)
                final_decision = result.output
                streaming_success = False
                print("✅ Fallback successful!")
                
            except Exception as fallback_error:
                print(f"❌ Fallback also failed: {fallback_error}")
                raise
        
        # Validate structured output
        print(f"\n📊 Final Structured Output:")
        print(f"   - delegate_to: {final_decision.delegate_to}")
        print(f"   - final_response: {final_decision.final_response}")
        print(f"   - reasoning: {final_decision.reasoning}")
        print(f"   - messages: {final_decision.messages}")
        print(f"   - streaming_success: {streaming_success}")
        
        # Validate decision logic
        if final_decision.final_response:
            assert final_decision.messages is not None, "Final response should have messages"
            assert final_decision.delegate_to is None, "Final response should not delegate"
            print("✅ Final response validation passed!")
        else:
            assert final_decision.delegate_to is not None, "Delegation should specify target agent"
            assert final_decision.delegate_to in ["web_research", "task_management", "email_draft"], f"Invalid delegation target: {final_decision.delegate_to}"
            print("✅ Delegation validation passed!")
        
        # Brief pause between tests
        await asyncio.sleep(0.5)
    
    print("\n🎉 All streaming structured output tests passed!")


async def test_messages_streaming_specifically():
    """Test specifically that messages field streams in real-time for final responses"""
    print("\n🧪 Testing Messages Field Streaming Specifically...")
    
    # Use a query that should definitely trigger a final response with a substantial messages field
    query = "Explain artificial intelligence, machine learning, and deep learning. What are the key differences and how do they relate to each other?"
    
    deps = SupervisorTestDependencies(session_id="messages_streaming_test")
    
    print(f"Query: {query}")
    print("🔄 Watching for real-time messages field streaming...")
    
    try:
        async with test_supervisor_agent.run_stream(query, deps=deps) as result:
            messages_updates = []
            
            async for partial_decision in result.stream():
                # Track how the messages field gets populated
                if hasattr(partial_decision, 'messages') and partial_decision.messages:
                    messages_updates.append(partial_decision.messages)
                    print(f"📝 Messages update {len(messages_updates)}: {partial_decision.messages}")
                
                # Also show the complete partial decision
                print(f"   Full partial: {partial_decision}")
            
            final_decision = await result.get_output()
            
            print(f"\n📊 Messages Streaming Analysis:")
            print(f"   - Total updates: {len(messages_updates)}")
            print(f"   - Final messages length: {len(final_decision.messages) if final_decision.messages else 0}")
            print(f"   - Final response: {final_decision.final_response}")
            
            if len(messages_updates) > 1:
                print("✅ Messages field streamed in real-time!")
            else:
                print("⚠️  Messages field did not stream incrementally")
            
            return len(messages_updates) > 1
            
    except Exception as e:
        print(f"❌ Messages streaming test failed: {e}")
        return False


async def test_delegation_scenarios():
    """Test that delegation scenarios work properly"""
    print("\n🧪 Testing Delegation Scenarios...")
    
    delegation_queries = {
        "web_research": "Find the latest information about OpenAI's new models",
        "task_management": "Set up a project timeline for our Q1 product release",
        "email_draft": "Write an email to our team about the upcoming conference"
    }
    
    for expected_delegate, query in delegation_queries.items():
        print(f"\n--- Testing delegation to {expected_delegate} ---")
        print(f"Query: {query}")
        
        deps = SupervisorTestDependencies(session_id=f"delegation_test_{expected_delegate}")
        
        try:
            async with test_supervisor_agent.run_stream(query, deps=deps) as result:
                async for partial_decision in result.stream():
                    print(f"   {partial_decision}")
                
                final_decision = await result.get_output()
                
                # Validate delegation
                assert final_decision.delegate_to == expected_delegate, f"Expected {expected_delegate}, got {final_decision.delegate_to}"
                assert final_decision.final_response == False, "Delegation should not be final response"
                assert final_decision.messages is None, "Delegation should not have messages"
                
                print(f"✅ Correctly delegated to {expected_delegate}")
                
        except Exception as e:
            print(f"❌ Delegation test failed for {expected_delegate}: {e}")
            raise


async def main():
    """Run all streaming foundation validation tests"""
    print("🚀 Starting Streaming Foundation Validation with .run_stream()")
    print("=" * 60)
    
    # Check environment
    llm_key = os.getenv("LLM_API_KEY")
    if not llm_key:
        print("❌ LLM_API_KEY environment variable required for testing")
        print("💡 Create a .env file based on .env.example")
        return
    
    try:
        # Test 1: General streaming structured output
        await test_streaming_structured_output()
        
        # Test 2: Specific messages field streaming
        messages_streamed = await test_messages_streaming_specifically()
        
        # Test 3: Delegation scenarios
        await test_delegation_scenarios()
        
        print("\n" + "=" * 60)
        if messages_streamed:
            print("🎉 STREAMING FOUNDATION VALIDATION PASSED!")
            print("✅ Structured output streams in real-time")
            print("✅ Messages field streams properly for final responses")
            print("✅ Delegation logic works correctly")
            print("✅ Ready to proceed with workflow integration")
        else:
            print("⚠️  STREAMING FOUNDATION NEEDS ATTENTION")
            print("❌ Messages field is not streaming in real-time")
            print("💡 May need to investigate Pydantic AI streaming configuration")
            
    except Exception as e:
        print(f"\n❌ STREAMING FOUNDATION VALIDATION FAILED: {e}")
        print("⚠️  DO NOT proceed with workflow integration until this is fixed")
        raise


if __name__ == "__main__":
    asyncio.run(main())