import logging
from google.adk.agents import LlmAgent
from google.adk.tools.tool_context import ToolContext
from google.cloud import bigquery

logger = logging.getLogger(__name__)

# Create a BigQuery client
bq_client = bigquery.Client()

def get_all_inventory(tool_context: ToolContext) -> dict[str, str]:
    """Gets all of the inventory of all items.  Will return a status code and a list 
    of rows with the inventory item id, other information, and item count.

    Unlike the get_item_inventory tool, this will return all items in the inventory via 
    the tool context state under key 'inventory'.  This is useful for caching the
    currently known inventory items without needing to query the database each time.

    Args:
        tool_context (ToolContext): The context of the tool being used.
    Returns:
        dict: A dictionary with the status information.
    """

    query = "SELECT * FROM `corporate_events.inventory`"
    query_job = bq_client.query(query)
    results = query_job.result()  # Wait for the job to complete.
    inventory = []
    for row in results:
        logger.info(row)
        inventory.append(dict(row.items()))

    tool_context.state['app:inventory'] = inventory
    return {"status": "success"}

def get_item_inventory(tool_context: ToolContext, product_id: str) -> dict:
    """Gets the inventory of a specific item.  If the item is in the database, it will 
    return a status code of success and a row with the inventory item id, other 
    information, and item count.
    If the item is not in the database, it will return a status code of success and
    a product value of None.
    If there are multiple items with the same product_id, it will return an error status.
    Args:
        tool_context (ToolContext): The context of the tool being used.
        product_id (str): The product ID of the item to get inventory for.
    Returns:
        dict: A dictionary with the status and product information.
        If the item is found, it will return a dictionary with "status": "success" and "product": row.
    """

    query = f"SELECT * FROM `corporate_events.inventory` WHERE product_id = @product_id LIMIT 1"
    query_job = bq_client.query(query, job_config=bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("product_id", "STRING", product_id)
        ]
    ))
    results = query_job.result()  # Wait for the job to complete.
    if (results.total_rows == 1):
        row = list(results)[0]
        return {
            "status": "success",
            "product": dict(row.items())
        }
    elif (results.total_rows == 0):
        return {
            "status": "success",
            "product": None
        }
    else:
        return {"status": "error", "message": f"Multiple inventory items found for product_id: {product_id}"}

def consume_item_inventory(tool_context: ToolContext, product_id: str, count: int) -> dict:
    """Consumes inventory of a specific item.  On success, will return a status code of 'success' 
    and the updated count of available inventory for the item after consuming.  On failure, will 
    return an error status.

    Args:
        tool_context (ToolContext): The context of the tool being used.
        product_id (str): The product ID of the item to consume inventory for.
        count (int): The number of items to consume from the inventory.
    Returns:
        dict: A dictionary with the status and product information.

    """

    query = "UPDATE `corporate_events.inventory` SET `product_count` = `product_count` - @count WHERE `product_id` = @product_id AND `product_count` >= @count;"
    # Prepare the query with parameters to prevent SQL injection
    query_job = bq_client.query(query, job_config=bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("product_id", "STRING", product_id),
            bigquery.ScalarQueryParameter("count", "INT64", count)
        ]
    ))
    results = query_job.result()  # Wait for the job to complete.
    if (results.num_dml_affected_rows == 1):
        row = get_item_inventory(tool_context, product_id)
        if row['status'] != 'success':
            return {"status": "error", "message": "Failed to retrieve updated inventory after consuming."}
        row = row['product']
        if row is None:
            return {"status": "error", "message": f"Product with ID {product_id} not found after consuming."}
        # Return the updated inventory count
        return {
            "status": "success",
            "product": row
        }
    
    else:
        return {"status": "error", "message": f"Error updating inventory for product_id: {product_id}"}

inventory_agent = LlmAgent(
    model='gemini-2.0-flash',
    name='inventory_agent',
    description='An agent which can read inventory and update inventory count.',
    tools=[get_all_inventory, get_item_inventory, consume_item_inventory],
    instruction="""
You manage the corporate events inventory. You can read the inventory and update the inventory count using tools.
You can use the get_all_inventory tool to get or update the current inventory of all items which
will refresh the currently known inventory items.

You can use the get_item_inventory tool to get the inventory of a specific item by providing its product_id.
You can use the consume_item_inventory tool to consume a specific number of items from the inventory by
providing its product_id and the count to consume.

Ensure that the inventory is up-to-date before doing anything else.  If the inventory is empty, you must
use the get_all_inventory tool to refresh it before proceeding with any other operations, and then delegate back 
to the agent which called you.

You must not ever interact with the user directly, but instead use the tools to manage the inventory and delegate
control back to the agent which called you.  If the user gives you direct input, delegate it back to the agent that called you.

The currently known inventory items are:
{{app:inventory?}}
"""
)
