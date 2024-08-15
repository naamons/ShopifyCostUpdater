import streamlit as st
import pandas as pd
import requests

# Function to fetch the inventory item ID by SKU
def fetch_inventory_item_id_by_sku(shop_name, access_token, sku):
    url = f"https://{shop_name}.myshopify.com/admin/api/2024-04/products.json?limit=250&fields=id,title,variants"
    headers = {
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": access_token
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        products = response.json().get('products', [])
        for product in products:
            for variant in product['variants']:
                if variant.get('sku') == sku:
                    return variant['inventory_item_id']
    else:
        st.error(f"Failed to fetch products: {response.status_code} - {response.text}")
    
    return None

# Function to update the cost of an inventory item
def update_inventory_item_cost(shop_name, access_token, inventory_item_id, cost):
    url = f"https://{shop_name}.myshopify.com/admin/api/2024-04/inventory_items/{inventory_item_id}.json"
    headers = {
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": access_token
    }
    data = {
        "inventory_item": {
            "id": inventory_item_id,
            "cost": cost
        }
    }
    response = requests.put(url, json=data, headers=headers)
    
    if response.status_code == 200:
        st.write(f"Successfully updated cost for inventory item ID {inventory_item_id} to {cost}.")
    else:
        st.error(f"Failed to update cost for inventory item ID {inventory_item_id}: {response.status_code} - {response.text}")

# Streamlit app layout
st.title("Shopify Inventory Cost Updater")

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

        # Process each row in the CSV
        for index, row in df.iterrows():
            sku = row['Part No.']
            cost = row['Cost']

            # Fetch the inventory item ID by SKU
            inventory_item_id = fetch_inventory_item_id_by_sku(shop_name, access_token, sku)
            if inventory_item_id:
                # Update the cost
                update_inventory_item_cost(shop_name, access_token, inventory_item_id, cost)
            else:
                st.error(f"Could not find inventory item for SKU {sku}")

else:
    st.info("Please upload a CSV file.")
