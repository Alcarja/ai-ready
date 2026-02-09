from google.adk.agents.llm_agent import Agent
from agent.tools import get_current_time, search_knowledge_base


root_agent = Agent(
    model='gemini-3-flash-preview',
    name='agent',
    description="Helpful assistant with access to current time information and a knowledge base",
    instruction="You are a helpful assistant. Use the 'get_current_time' tool to answer questions about the current time in cities. Use the 'search_knowledge_base' tool to search for information in the knowledge base. Always provide helpful and accurate responses.",
    tools=[get_current_time, search_knowledge_base],
)
