import streamlit as st
import pandas as pd
import requests
import time

# Function to search for an inventory item by SKU
def search_inventory_item_by_sku(shop_name, access_token, sku):
    # Initial API call to fetch products with variants
    url = f"https://{shop_name}.myshopify.com/admin/api/2024-01/products.json?limit=250"
    headers = {
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": access_token
    }
    page_info = None
    found_item = None

    while True:
        if page_info:
            url += f"&page_info={page_info}"
        
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            st.error(f"Failed to fetch products: {response.status_code} - {response.text}")
            return None
        
        products = response.json().get('products', [])
        
        # Search through products and their variants
        for product in products:
            for variant in product['variants']:
                if variant['sku'].strip() == sku.strip():
                    found_item = {
                        'product_id': product['id'],
                        'variant_id': variant['id'],
                        'inventory_item_id': variant['inventory_item_id']
                    }
                    break
            if found_item:
                break
        
        if found_item or not response.headers.get('Link'):
            break

        # Handle pagination
        link_header = response.headers.get('Link')
        if link_header and 'rel="next"' in link_header:
            page_info = link_header.split('page_info=')[1].split('>')[0]
        else:
            break
        
        time.sleep(0.5)  # Respect API rate limits
    
    return found_item

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

            # Search for the inventory item by SKU
            inventory_item = search_inventory_item_by_sku(shop_name, access_token, sku)
            if inventory_item:
                simulate_update_unit_cost(inventory_item['inventory_item_id'], cost)
                simulated_count += 1
            else:
                st.error(f"Could not find inventory item for SKU {sku}")

        st.success(f"Simulated cost updates for {simulated_count} SKUs.")

else:
    st.info("Please upload a CSV file.")
