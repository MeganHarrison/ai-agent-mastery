from pydantic_ai import Agent
import streamlit as st
import asyncio
import os

from agent import agent

# Import all the message part classes from Pydantic AI
from pydantic_ai.messages import (
    ModelMessage, ModelRequest, ModelResponse, TextPart, 
    UserPromptPart, PartDeltaEvent, PartStartEvent, TextPartDelta
)

def display_message_part(part):
    """
    Display a single part of a message in the Streamlit UI.
    Customize how you display system prompts, user prompts,
    tool calls, tool returns, etc.
    """
    # User messages
    if part.part_kind == 'user-prompt':
        with st.chat_message("user"):
            st.markdown(part.content)
    # AI messages
    elif part.part_kind == 'text':
        with st.chat_message("assistant"):
            st.markdown(part.content)             

async def run_agent_with_streaming(user_input):
    async with agent.iter(user_input, message_history=st.session_state.messages) as run:
        async for node in run:
            ai_response = ""
            if Agent.is_model_request_node(node):
                # A model request node => We can stream tokens from the model's request
                async with node.stream(run.ctx) as request_stream:
                    async for event in request_stream:
                        if isinstance(event, PartStartEvent) and event.part.part_kind == 'text':
                                ai_response = event.part.content
                                yield ai_response
                        elif isinstance(event, PartDeltaEvent) and isinstance(event.delta, TextPartDelta):
                                delta = event.delta.content_delta
                                ai_response += delta
                                yield delta         

    # Add the new messages to the chat history (including tool calls and responses)
    st.session_state.messages.extend(run.result.new_messages())


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~ Main Function with UI Creation ~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

async def main():
    st.title("Pydantic AI Agent")

    # Initialize chat history in session state if not present
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display all messages from the conversation so far
    # Each message is either a ModelRequest or ModelResponse.
    # We iterate over their parts to decide how to display them.
    for msg in st.session_state.messages:
        if isinstance(msg, ModelRequest) or isinstance(msg, ModelResponse):
            for part in msg.parts:
                display_message_part(part)

    # Chat input for the user
    user_input = st.chat_input("What do you want to do today?")

    if user_input:
        # Display user prompt in the UI
        with st.chat_message("user"):
            st.markdown(user_input)

        # Display the assistant's partial response while streaming
        with st.chat_message("assistant"):
            # Create a placeholder for the streaming text
            message_placeholder = st.empty()
            full_response = ""
            
            # Properly consume the async generator with async for
            generator = run_agent_with_streaming(user_input)
            async for message in generator:
                full_response += message
                message_placeholder.markdown(full_response + "▌")
            
            # Final response without the cursor
            message_placeholder.markdown(full_response)


if __name__ == "__main__":
    asyncio.run(main())
