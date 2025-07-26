"""
Streamlit UI for the Supervisor Pattern Multi-Agent System.

This provides an intuitive interface for interacting with the supervisor agent 
that dynamically delegates to specialized sub-agents with real-time streaming.
"""
import streamlit as st
import asyncio
import uuid
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import LangGraph workflow and dependencies
from graph.workflow import workflow, create_api_initial_state, extract_api_response_data

# Page configuration
st.set_page_config(
    page_title="Supervisor Agent System",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for supervisor pattern UI
st.markdown("""
<style>
    .stMarkdown h3 {
        margin-top: 1rem;
        margin-bottom: 0.5rem;
        color: #1f77b4;
    }
    .supervisor-response {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid #1f77b4;
    }
    .delegation-info {
        background-color: #e3f2fd;
        border: 1px solid #90caf9;
        color: #1565c0;
        padding: 0.75rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .shared-state-item {
        background-color: #f5f5f5;
        border-left: 3px solid #4caf50;
        padding: 0.5rem;
        margin: 0.25rem 0;
        border-radius: 0.25rem;
    }
    .main-header {
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-container {
        max-width: 900px;
        margin: 0 auto;
    }
    .iteration-badge {
        background-color: #ff9800;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 1rem;
        font-size: 0.75rem;
        font-weight: bold;
    }
    .agent-badge {
        background-color: #4caf50;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-size: 0.75rem;
        font-weight: bold;
        margin-right: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())


async def stream_supervisor_response(query: str, session_id: str):
    """
    Stream response from the supervisor pattern workflow.
    
    Args:
        query: User's query
        session_id: Session identifier
        
    Returns:
        Tuple of (full_response, workflow_metadata)
    """
    # Create initial state for supervisor workflow
    initial_state = create_api_initial_state(
        query=query,
        session_id=session_id,
        request_id=str(uuid.uuid4()),
        pydantic_message_history=[]
    )
    
    # Create workflow configuration
    thread_id = f"supervisor-agent-{session_id}"
    config = {"configurable": {"thread_id": thread_id}}
    
    # Create placeholders for real-time updates
    response_placeholder = st.empty()
    delegation_placeholder = st.empty()
    shared_state_placeholder = st.empty()
    
    full_response = ""
    workflow_metadata = {}
    current_delegation = None
    shared_state_items = []
    
    try:
        # Stream the supervisor workflow
        async for chunk in workflow.astream(initial_state, config, stream_mode="updates"):
            for node_name, node_output in chunk.items():
                
                # Handle supervisor node outputs
                if node_name == "supervisor_node":
                    if node_output.get("supervisor_reasoning"):
                        current_delegation = {
                            "reasoning": node_output["supervisor_reasoning"],
                            "delegate_to": node_output.get("delegate_to"),
                            "iteration": node_output.get("iteration_count", 0),
                            "workflow_complete": node_output.get("workflow_complete", False)
                        }
                        
                        # Update delegation info
                        delegation_placeholder.markdown(
                            format_delegation_info(current_delegation)
                        )
                    
                    # Handle final response streaming
                    if node_output.get("final_response"):
                        full_response = node_output["final_response"]
                        response_placeholder.markdown(f"**Final Response:**\n\n{full_response}")
                
                # Handle sub-agent outputs
                elif node_name in ["web_research_node", "task_management_node", "email_draft_node"]:
                    if node_output.get("shared_state"):
                        shared_state_items = node_output["shared_state"]
                        shared_state_placeholder.markdown(
                            format_shared_state(shared_state_items)
                        )
                
                # Real-time UI updates
                await asyncio.sleep(0.1)  # Small delay for smooth updates
        
        # Get final state for metadata
        final_state = workflow.get_state(config).values
        if final_state:
            workflow_metadata = extract_api_response_data(final_state)
        
        return full_response, workflow_metadata
        
    except Exception as e:
        st.error(f"Error in supervisor workflow: {str(e)}")
        return f"Error: {str(e)}", {}


def format_delegation_info(delegation: Dict[str, Any]) -> str:
    """Format delegation information for display."""
    if not delegation:
        return ""
    
    iteration_badge = f'<span class="iteration-badge">Iteration {delegation["iteration"]}</span>'
    
    if delegation["workflow_complete"]:
        status = "🎯 **Workflow Complete** - Supervisor providing final response"
    elif delegation["delegate_to"]:
        agent_map = {
            "web_research": "🔍 Web Research Agent",
            "task_management": "📋 Task Management Agent", 
            "email_draft": "✉️ Email Draft Agent"
        }
        agent_name = agent_map.get(delegation["delegate_to"], delegation["delegate_to"])
        status = f"🚀 **Delegating to:** {agent_name}"
    else:
        status = "🤔 **Analyzing request...**"
    
    reasoning = delegation.get("reasoning", "")
    
    return f"""
    <div class="delegation-info">
        {iteration_badge}
        <br><br>
        {status}
        <br><br>
        <strong>Reasoning:</strong> {reasoning}
    </div>
    """


def format_shared_state(shared_state: List[str]) -> str:
    """Format shared state for display."""
    if not shared_state:
        return ""
    
    items_html = ""
    for item in shared_state:
        # Extract agent type from prefix
        agent_type = "Unknown"
        if item.startswith("Web Research:"):
            agent_type = "🔍 Web Research"
        elif item.startswith("Task Management"):
            agent_type = "📋 Task Management"
        elif item.startswith("Email Draft:"):
            agent_type = "✉️ Email Draft"
        
        items_html += f"""
        <div class="shared-state-item">
            <span class="agent-badge">{agent_type}</span>
            {item}
        </div>
        """
    
    return f"""
    <div style="margin-top: 1rem;">
        <strong>🔗 Shared State (Agent Communication):</strong>
        {items_html}
    </div>
    """


def display_workflow_metadata(metadata: Dict[str, Any]):
    """Display comprehensive workflow metadata."""
    if not metadata:
        return
    
    with st.expander("🎯 Supervisor Workflow Details", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Agent Type", metadata.get("agent_type", "unknown").title())
            st.metric("Workflow Complete", 
                     "✅ Yes" if metadata.get("workflow_complete") else "❌ No")
        
        with col2:
            st.metric("Iterations", metadata.get("iteration_count", 0))
            shared_state = metadata.get("shared_state", [])
            st.metric("Shared State Items", len(shared_state))
        
        with col3:
            st.metric("Session ID", metadata.get("session_id", "Unknown")[:8] + "...")
            st.metric("Request ID", metadata.get("request_id", "Unknown")[:8] + "...")
        
        # Display supervisor reasoning
        if metadata.get("supervisor_reasoning"):
            st.markdown("**🧠 Supervisor Reasoning:**")
            st.info(metadata["supervisor_reasoning"])
        
        # Display shared state details
        if shared_state:
            st.markdown("**🔗 Agent Communication Log:**")
            for i, item in enumerate(shared_state, 1):
                st.markdown(f"{i}. {item}")


def main():
    """Main Streamlit application."""
    
    # Header
    st.markdown('<div class="main-header">', unsafe_allow_html=True)
    st.title("🎯 Supervisor Agent System")
    st.markdown("Intelligent multi-agent coordination with real-time streaming")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Chat container
    with st.container():
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        
        # Display chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                
                # Display workflow metadata if available
                if message["role"] == "assistant" and "metadata" in message:
                    display_workflow_metadata(message["metadata"])
        
        # Chat input
        if prompt := st.chat_input("Ask me anything - I'll intelligently delegate or respond directly..."):
            # Add user message to history
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Display assistant response with streaming
            with st.chat_message("assistant"):
                try:
                    # Run the async streaming function
                    response, metadata = asyncio.run(
                        stream_supervisor_response(prompt, st.session_state.session_id)
                    )
                    
                    # Add assistant message to history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response,
                        "metadata": metadata
                    })
                    
                    # Display workflow metadata
                    display_workflow_metadata(metadata)
                    
                except Exception as e:
                    error_msg = f"Error in supervisor workflow: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg,
                        "metadata": {}
                    })
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Sidebar with session info and examples
    with st.sidebar:
        st.header("🎯 Supervisor Agent")
        st.text(f"Session: {st.session_state.session_id[:8]}...")
        
        if st.button("🔄 New Session"):
            st.session_state.messages = []
            st.session_state.session_id = str(uuid.uuid4())
            st.rerun()
        
        if st.button("🗑️ Clear History"):
            st.session_state.messages = []
            st.rerun()
        
        st.divider()
        
        # Example queries
        st.markdown("""
        ### 💡 Example Queries
        
        **🔍 Web Research:**
        - "Research the latest AI safety developments"
        - "Find Tesla's latest quarterly earnings"
        - "What are current renewable energy trends?"
        
        **📋 Task Management:**
        - "Create a project plan for Q1 launch"
        - "Set up tasks for marketing campaign"
        - "Organize development timeline"
        
        **✉️ Email Drafting:**
        - "Draft email to investors about Q4 results"
        - "Write outreach email for partnerships"
        - "Compose client update email"
        
        **🎯 Direct Response:**
        - "What is machine learning?"
        - "Explain neural networks"
        - "How does AI work?"
        """)
        
        st.divider()
        
        # Architecture info
        st.markdown("""
        ### 🏗️ Architecture
        
        **Supervisor Pattern:**
        - Intelligent request analysis
        - Dynamic agent delegation
        - Real-time streaming responses
        - Shared state coordination
        
        **Sub-Agents:**
        - 🔍 Web Research (Brave API)
        - 📋 Task Management (Asana API)
        - ✉️ Email Draft (Gmail API)
        """)
        
        st.divider()
        st.caption("Powered by Pydantic AI, LangGraph & Supervisor Pattern")


if __name__ == "__main__":
    main()