import streamlit as st
import pandas as pd
import requests
import time

# Function to fetch all products and their variant SKUs
def fetch_all_product_variants(shop_name, access_token):
    page_info = None
    headers = {
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": access_token
    }
    all_variants = []

    while True:
        url = f"https://{shop_name}.myshopify.com/admin/api/2024-04/products.json?limit=250&fields=id,title,variants"
        if page_info:
            url += f"&page_info={page_info}"
        
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
        
        link_header = response.headers.get('Link')
        if link_header and 'rel="next"' in link_header:
            page_info = link_header.split('page_info=')[1].split('>')[0]
        else:
            break
        
        time.sleep(0.5)  # Respect API rate limits

    return pd.DataFrame(all_variants)

# Streamlit app layout
st.title("Shopify Products and Variants Viewer")

# Accessing Shopify credentials from Streamlit secrets
shop_name = st.secrets["shop_name"]
access_token = st.secrets["access_token"]

# Fetch and display product variants
if st.button("Fetch Products and Variants"):
    with st.spinner("Fetching data..."):
        variants_df = fetch_all_product_variants(shop_name, access_token)
        if variants_df is not None:
            st.success("Data fetched successfully!")
            st.write("### Product Variants")
            st.dataframe(variants_df)
        else:
            st.error("Failed to fetch data. Please check your credentials and try again.")
