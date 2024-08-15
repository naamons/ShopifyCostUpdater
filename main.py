import streamlit as st
import pandas as pd
import requests

# Shopify API endpoints
BASE_URL = f"https://{st.secrets.shop_name}.myshopify.com/admin/api/2023-04"
PRODUCTS_URL = f"{BASE_URL}/products.json"
INVENTORY_ITEM_URL = f"{BASE_URL}/inventory_items"

def get_all_products():
    products = []
    url = PRODUCTS_URL
    while url:
        response = requests.get(url, headers={"X-Shopify-Access-Token": st.secrets.access_token})
        data = response.json()
        products.extend(data['products'])
        url = response.links.get('next', {}).get('url')
    return products

def update_product_cost(inventory_item_id, cost):
    url = f"{INVENTORY_ITEM_URL}/{inventory_item_id}.json"
    payload = {
        "inventory_item": {
            "cost": cost
        }
    }
    response = requests.put(url, json=payload, headers={"X-Shopify-Access-Token": st.secrets.access_token})
    return response.status_code == 200

def main():
    st.title("Shopify Product Cost Updater")

    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.write("Uploaded CSV:")
        st.write(df)

        if st.button("Update Costs"):
            products = get_all_products()
            
            updated_count = 0
            for _, row in df.iterrows():
                sku = row['Part No.']
                cost = row['Cost']
                
                for product in products:
                    for variant in product['variants']:
                        if variant['sku'] == sku:
                            if update_product_cost(variant['inventory_item_id'], cost):
                                updated_count += 1
                            break
            
            st.success(f"Updated costs for {updated_count} products.")

if __name__ == "__main__":
    main()
