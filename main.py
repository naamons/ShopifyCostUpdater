import streamlit as st
import pandas as pd
import requests

# Function to fetch the first 10 products and their variant SKUs
def fetch_first_10_product_variants(shop_name, access_token):
    headers = {
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": access_token
    }
    all_variants = []

    url = f"https://{shop_name}.myshopify.com/admin/api/2024-04/products.json?limit=10&fields=id,title,variants"
    
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        st.error(f"Failed to fetch products: {response.status_code} - {response.text}")
        return None
    
    products = response.json().get('products', [])
    
    for product in products:
        for variant in product['variants']:
            all_variants.append({
                'Product ID': product['id'],
                'Product Title': product['title'],
                'Variant ID': variant['id'],
                'SKU': variant.get('sku'),
                'Inventory Item ID': variant['inventory_item_id']
            })
    
    return pd.DataFrame(all_variants)

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
st.title("Shopify Products and Cost Updater")

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

        # Fetch and display product variants
        if st.button("Fetch and Compare"):
            with st.spinner("Fetching data..."):
                variants_df = fetch_first_10_product_variants(shop_name, access_token)
                if variants_df is not None:
                    st.success("Data fetched successfully!")
                    st.write("### First 10 Product Variants")
                    st.dataframe(variants_df)

                    # Compare SKUs and update costs
                    for index, row in df.iterrows():
                        sku = row['Part No.']
                        cost = row['Cost']
                        matching_variant = variants_df[variants_df['SKU'] == sku]

                        if not matching_variant.empty:
                            inventory_item_id = matching_variant.iloc[0]['Inventory Item ID']
                            update_inventory_item_cost(shop_name, access_token, inventory_item_id, cost)
                        else:
                            st.error(f"Could not find matching SKU in Shopify for Part No. {sku}")

else:
    st.info("Please upload a CSV file.")
