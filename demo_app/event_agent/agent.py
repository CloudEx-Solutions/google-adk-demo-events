import logging

from google.adk.agents import Agent, SequentialAgent
from .agents.inventory import inventory_agent
from .agents.suggestor import suggestor_agent
from .agents.checkout import checkout_agent
from google.adk.tools.agent_tool import AgentTool

logger = logging.getLogger(__name__)

root_agent = Agent(
    model='gemini-2.0-flash',
    name='root_agent',
    description='An agent which can plan and run events, supported by subagents.',
    sub_agents=[suggestor_agent, checkout_agent],
    tools=[],
    instruction="""
You are a corporate events planner.

You will greet the user by briefly describing what you can do, and then immediately delegating
to the suggestor agent to make suggestions for the event based on the user's needs.

You must not interact with the user directly beyond that initial greeting, 
instead delegating to sub-agents.

For any event planning related requests, you will delegate to the suggestor agent.
For running an event you will delegate to the checkout agent.
"""
)
