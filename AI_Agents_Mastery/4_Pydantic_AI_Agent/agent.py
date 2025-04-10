from dotenv import load_dotenv
import os

from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.mcp import MCPServerStdio
from pydantic_ai import Agent, RunContext

from prompt import AGENT_SYSTEM_PROMPT

load_dotenv()

# ========== Helper function to get model configuration ==========
def get_model():
    llm = os.getenv('LLM_CHOICE', 'gpt-4o-mini')
    base_url = os.getenv('LLM_BASE_URL', 'https://api.openai.com/v1')
    api_key = os.getenv('LLM_API_KEY', 'no-api-key-provided')

    return OpenAIModel(llm, provider=OpenAIProvider(base_url=base_url, api_key=api_key))

# ========== Pydantic AI Agent ==========
agent = Agent(
    get_model(),
    system_prompt=AGENT_SYSTEM_PROMPT
)