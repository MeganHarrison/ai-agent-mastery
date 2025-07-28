"""
Streamlit UI for the Human-in-the-Loop Email Agent.

This provides an intuitive interface for interacting with the email agent
that can read inbox, draft emails, and requires human approval for sending.
"""
import streamlit as st
import asyncio
import uuid
from dotenv import load_dotenv
import httpx
import json
import os

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Email Agent Assistant",
    page_icon="✉️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "awaiting_approval" not in st.session_state:
    st.session_state.awaiting_approval = False
if "email_preview" not in st.session_state:
    st.session_state.email_preview = None


async def stream_agent_response(query: str, session_id: str, user_token: str):
    """
    Stream response from the email agent API.
    
    Args:
        query: User's query
        session_id: Session identifier
        user_token: User authentication token
        
    Returns:
        Tuple of (full_response, email_preview_data)
    """
    api_url = os.getenv("API_URL", "http://localhost:8002")
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{api_url}/api/human-in-the-loop-agent",
            json={
                "query": query,
                "session_id": session_id,
                "request_id": str(uuid.uuid4()),
                "user_id": "demo_user"  # In production, get from auth
            },
            headers={
                "Authorization": f"Bearer {user_token}"
            },
            timeout=60.0
        )
        
        full_response = ""
        email_preview = None
        
        async for line in response.aiter_lines():
            if line:
                try:
                    # Skip empty lines
                    if not line.strip():
                        continue
                    
                    chunk = json.loads(line)
                    
                    # Handle text streaming
                    if "text" in chunk:
                        full_response = chunk["text"]
                        yield full_response, None
                    
                    # Handle email approval request
                    elif chunk.get("type") == "approval_request":
                        email_preview = chunk.get("email_preview")
                        yield full_response, email_preview
                    
                    # Handle completion
                    elif chunk.get("complete"):
                        yield full_response, email_preview
                        
                except json.JSONDecodeError:
                    continue
                except Exception:
                    continue


def display_email_preview(email_data):
    """Display email preview for approval."""
    st.info("📧 **Email Ready for Approval**")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("**Recipients:** " + ", ".join(email_data.get("recipients", [])))
        st.markdown("**Subject:** " + email_data.get("subject", ""))
        st.markdown("**Body:**")
        st.text_area("", value=email_data.get("body", ""), height=200, disabled=True)
    
    with col2:
        if st.button("✅ Approve & Send", type="primary", use_container_width=True):
            return "yes"
        if st.button("❌ Cancel", type="secondary", use_container_width=True):
            return "no"
        if st.button("✏️ Revise", use_container_width=True):
            feedback = st.text_input("What changes would you like?")
            if feedback:
                return f"no-{feedback}"
    
    return None


def main():
    """Main Streamlit application."""
    
    # Header
    st.title("✉️ Email Agent Assistant")
    st.markdown("AI-powered email management with human approval for sending")
    
    # Get user token (in production, implement proper auth)
    user_token = os.getenv("DEMO_USER_TOKEN", "demo_token")
    
    # Chat container
    with st.container():
        
        # Display chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                if message.get("email_preview"):
                    # Show email preview
                    display_email_preview(message["email_preview"])
                else:
                    st.markdown(message["content"])
        
        # Handle email approval if needed
        if st.session_state.awaiting_approval and st.session_state.email_preview:
            with st.chat_message("assistant"):
                decision = display_email_preview(st.session_state.email_preview)
                
                if decision:
                    # Send approval decision
                    st.session_state.awaiting_approval = False
                    approval_query = decision
                    if decision.startswith("no-"):
                        approval_query = decision
                    
                    # Add approval message
                    st.session_state.messages.append({
                        "role": "user",
                        "content": f"Decision: {decision}"
                    })
                    
                    # Process approval
                    st.rerun()
        
        # Chat input
        if prompt := st.chat_input("Ask me to check emails, draft responses, or manage your inbox..."):
            # Add user message to history
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Display assistant response with streaming
            with st.chat_message("assistant"):
                response_placeholder = st.empty()
                
                try:
                    # Run the async streaming function
                    full_response = ""
                    email_preview = None
                    
                    async def get_response():
                        nonlocal full_response, email_preview
                        async for response, preview in stream_agent_response(
                            prompt, 
                            st.session_state.session_id,
                            user_token
                        ):
                            full_response = response
                            if preview:
                                email_preview = preview
                            response_placeholder.markdown(response)
                    
                    asyncio.run(get_response())
                    
                    # Check if we need approval
                    if email_preview:
                        st.session_state.awaiting_approval = True
                        st.session_state.email_preview = email_preview
                        st.rerun()
                    
                    # Add assistant message to history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": full_response,
                        "email_preview": email_preview
                    })
                    
                except Exception as e:
                    error_msg = f"Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })
    
    # Sidebar with session info and examples
    with st.sidebar:
        st.header("✉️ Email Assistant")
        st.text(f"Session: {st.session_state.session_id[:8]}...")
        
        if st.button("🔄 New Session"):
            st.session_state.messages = []
            st.session_state.session_id = str(uuid.uuid4())
            st.session_state.awaiting_approval = False
            st.session_state.email_preview = None
            st.rerun()
        
        if st.button("🗑️ Clear History"):
            st.session_state.messages = []
            st.session_state.awaiting_approval = False
            st.session_state.email_preview = None
            st.rerun()
        
        st.divider()
        
        # Example queries
        st.markdown("""
        ### 💡 Example Queries
        
        **📥 Reading Emails:**
        - "Check my inbox for new emails"
        - "Show me unread emails"
        - "Any emails from John?"
        
        **✍️ Drafting Emails:**
        - "Draft a reply to the latest email"
        - "Create an email to team about meeting"
        - "Write a follow-up email"
        
        **📤 Sending Emails:**
        - "Send an email to alice@example.com"
        - "Email the team about project update"
        - "Reply to Bob's email"
        """)
        
        st.divider()
        
        # Architecture info
        st.markdown("""
        ### 🏗️ Architecture
        
        **Human-in-the-Loop:**
        - Autonomous email reading
        - Intelligent draft creation
        - Required approval for sending
        - LangGraph interrupt pattern
        
        **Features:**
        - 📥 Gmail inbox integration
        - ✍️ Smart email drafting
        - 🔒 Human approval workflow
        - 💾 Conversation memory
        """)
        
        st.divider()
        st.caption("Powered by Pydantic AI & LangGraph")


if __name__ == "__main__":
    main()