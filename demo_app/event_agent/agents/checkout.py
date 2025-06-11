import logging
from google.adk.agents import LlmAgent
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.agent_tool import AgentTool
from .inventory import inventory_agent
from .suggestor import suggestor_agent

logger = logging.getLogger(__name__)



checkout_agent = LlmAgent(
    model='gemini-2.0-flash',
    name='checkout_agent',
    description='An agent which can checkout the cart and run the event.',
    tools=[AgentTool(inventory_agent), AgentTool(suggestor_agent)],
    instruction="""
If the cart is empty then pass control on to the root agent (unless you are running an event - in which case you may proceed with your existing instructions).

Otherwise, to run the event you will need to ensure that the inventory is up-to-date (using the inventory agent)
and has enough consumable items based on the contents of the current cart.  
If not, pass control to the suggestor agent to make suggestions for which inventory items to use.

Then you will use the inventory agent tool consume the count needed for each item in the cart.  These function calls 
should be executed in parallel to speed up the process.

After the event is run, you will clear the cart using the clear cart tool from the suggestor agent and also 
use the inventory agent to get all inventory items, to prepare for the next event.  These calls should be executed in parallel as well.

You will then present the event that was run by generating a description of the event and how the products were used.  

Do not interact with the user to tell him what you are doing in the background. 

The currently known inventory items are:
{{app:inventory?}}

The current cart is:
{{user:cart?}}
"""
)
