import os

from pydantic_ai import Agent

from src.agent.context import AgentContext
from src.agent.prompt import get_system_prompt
from src.agent.tools.query_data import query_data
from src.agent.tools.visualize import visualize


def create_agent(dataset_info: str) -> Agent[AgentContext]:
    """Create the data analysis agent with query and visualization tools."""
    model = os.getenv("MODEL", "anthropic:claude-haiku-4-5-20251001")

    agent: Agent[AgentContext] = Agent(
        model=model,
        deps_type=AgentContext,
        system_prompt=get_system_prompt(dataset_info),
        retries=3,
    )

    agent.tool(query_data)
    agent.tool(visualize)

    return agent
