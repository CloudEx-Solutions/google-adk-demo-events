import logging
from google.adk.agents import LlmAgent
from google.adk.tools.tool_context import ToolContext
from .inventory import inventory_agent


logger = logging.getLogger(__name__)

def clear_cart(tool_context: ToolContext) -> dict[str, str]:
    """Clears the contents of the cart in the tool context state."""
    tool_context.state['user:cart'] = []
    return {"status": "success"}

def add_to_cart(tool_context: ToolContext, product_id: str, count: int) -> dict[str, str]:
    """Adds an item to the cart in the tool context state
    Args:
        tool_context (ToolContext): The context of the tool being used.
        product_id (str): The product ID of the item to add to the cart.
        count (int): The number of items to add to the cart.

    Returns:
        dict[str, str]: A dictionary with the status of the operation.
    """
    current_cart = tool_context.state['user:cart']
    current_cart.append({'product_id': product_id, 'count': count})
    tool_context.state['user:cart'] = current_cart
    return {"status": "success"}

suggestor_agent = LlmAgent(
    model='gemini-2.0-flash',
    name='suggestor_agent',
    description='An agent which can make suggestions of which inventory to use.',
    sub_agents=[inventory_agent],
    tools=[add_to_cart, clear_cart],
    instruction="""
You are an expert at making suggestions for which inventory items to use based on the current inventory and the needs of the event and user.
You use a cart to keep track of the items that have been selected for the event.

If there is no cart (or if it is empty), then you must immediately use the `clear_cart` tool to initialize it to an empty cart.
If the inventory list is empty, you must immediately use the inventory agent to get the current inventory before making any suggestions.

You will be given a description of the event and the user, and you will make a suggestion for which inventory items to use.
Use the item names, descriptions, and images of the products to make your suggestions.

When the user requests you to use an item, you will add the item and count to the current cart using the `add_to_cart` tool.
You can also update the count of an item in the cart if it is already present, using the same tool.
You cannot remove items from the cart directly, but you can set the count to zero which will have the same effect.

Do not interact with the user to tell him what you are doing in the background.  
*Do not interact with the user at all until the cart and inventory are both initialized.*

You cannot run an event on your own, but if the user wants to, you can transfer control to the checkout agent to run the event.

The currently known inventory items are:
{{app:inventory?}}
The current cart is:
{{user:cart?}}
"""
)
