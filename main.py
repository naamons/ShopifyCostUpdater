import streamlit as st
import pandas as pd
import requests
import time

# Function to fetch products with pagination
def fetch_products(shop_name, access_token, page_info=None):
    url = f"https://{shop_name}.myshopify.com/admin/api/2024-01/products.json?limit=250"
    if page_info:
        url += f"&page_info={page_info}"
    
    headers = {
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": access_token
    }
    response = requests.get(url, headers=headers)
    products = response.json().get('products', [])
    next_page_info = response.headers.get('Link', None)
    
    if next_page_info and 'rel="next"' in next_page_info:
        next_page_info = next_page_info.split(';')[0].split('page_info=')[1].strip('<>')
    else:
        next_page_info = None

    return products, next_page_info

# Function to fetch the inventory item ID for a given variant SKU
def fetch_inventory_item_id(shop_name, access_token, sku):
    page_info = None
    while True:
        products, page_info = fetch_products(shop_name, access_token, page_info)
        for product in products:
            for variant in product['variants']:
                if variant['sku'] == sku:
                    return variant['inventory_item_id']
        if not page_info:
            break
        time.sleep(0.5)  # Respect rate limits
    return None

# Function to simulate updating the unit cost for a given inventory item ID
def simulate_update_unit_cost(inventory_item_id, cost):
    # Simulate the update by logging the action instead of making an actual API request
    st.write(f"Would update inventory item ID {inventory_item_id} with cost {cost}.")

# Streamlit app layout
st.title("Shopify Unit Cost Updater (Dry Run)")

# Accessing Shopify credentials from Streamlit secrets
shop_name = st.secrets["shop_name"]
access_token = st.secrets["access_token"]

# Upload CSV file
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file:
    # Read the uploaded CSV
    df = pd.read_csv(uploaded_file)

    # Validate that required columns exist
    if "Part No." not in df.columns or "Cost" not in df.columns:
        st.error("CSV must contain 'Part No.' and 'Cost' columns.")
    else:
        st.success("CSV file loaded successfully!")
        st.write("Preview of CSV data:")
        st.write(df.head())

        # Simulate the update process
        st.write("Simulating cost updates in Shopify...")
        simulated_count = 0
        for index, row in df.iterrows():
            sku = row['Part No.']
            cost = row['Cost']

            # Fetch the inventory item ID
            inventory_item_id = fetch_inventory_item_id(shop_name, access_token, sku)
            if inventory_item_id:
                simulate_update_unit_cost(inventory_item_id, cost)
                simulated_count += 1
            else:
                st.error(f"Could not find inventory item for SKU {sku}")

        st.success(f"Simulated cost updates for {simulated_count} SKUs.")

else:
    st.info("Please upload a CSV file.")
