import streamlit as st
import pandas as pd
import requests
import time

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
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            results_area = st.empty()
            
            updated_count = 0
            total_count = len(df)
            results = []

            for index, row in df.iterrows():
                sku = row['Part No.']
                cost = row['Cost']
                
                status_text.text(f"Processing SKU: {sku}")
                
                found = False
                for product in products:
                    for variant in product['variants']:
                        if variant['sku'] == sku:
                            if update_product_cost(variant['inventory_item_id'], cost):
                                updated_count += 1
                                results.append(f"✅ Updated: SKU {sku}, New Cost: {cost}")
                            else:
                                results.append(f"❌ Failed to update: SKU {sku}")
                            found = True
                            break
                    if found:
                        break
                
                if not found:
                    results.append(f"⚠️ Not found: SKU {sku}")
                
                progress_bar.progress((index + 1) / total_count)
                results_area.text("\n".join(results))
                time.sleep(0.1)  # Small delay to make updates visible
            
            status_text.text("Update Completed")
            st.success(f"Updated costs for {updated_count} out of {total_count} products.")

if __name__ == "__main__":
    main()
