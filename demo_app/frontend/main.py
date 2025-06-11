import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh
from google.cloud import bigquery

# Create a BigQuery client
bq_client = bigquery.Client()

@st.cache_data(ttl=0)
def get_bigquery_data(query: str):
    """Fetch data from BigQuery."""
    query_job = bq_client.query(query)
    results = query_job.result()  # Wait for the job to complete.
    return results.to_dataframe()

# Refresh the page
count = st_autorefresh(interval=5000, limit=1000, key="refresh_counter")

st.write("Inventory Data")
st.dataframe(get_bigquery_data("SELECT `product_name` as Name, `product_count` as Count FROM `corporate_events.inventory` LIMIT 10"))  # Adjust the query as needed
