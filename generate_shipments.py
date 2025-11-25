import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Set seed for reproducibility
np.random.seed(42)
random.seed(42)

# Parameters
num_products = 250
num_stores = 26
num_dates = 30  # 30 days of data

# Create product names
products = [f"Product_{i:03d}" for i in range(1, num_products + 1)]

# Create store names
stores = [f"Store_{chr(65 + i)}" for i in range(num_stores)]

# Generate date range
start_date = datetime(2024, 1, 1)
dates = [start_date + timedelta(days=d) for d in range(num_dates)]

# Create data records
records = []

for date in dates:
    for store in stores:
        # Each store carries 60-120 random products (not all products)
        num_products_in_store = random.randint(60, 120)
        store_products = random.sample(products, num_products_in_store)
        
        for product in store_products:
            # Normal shipment quantity: 5-50 units
            quantity = random.randint(5, 50)
            
            # Inject anomalies (2% chance)
            if random.random() < 0.02:
                # Anomaly 1: Extremely high shipment (10x normal)
                if random.random() < 0.5:
                    quantity = random.randint(500, 1000)
                # Anomaly 2: Negative quantity (data error)
                else:
                    quantity = -random.randint(10, 50)
            
            # Price per unit: 10-500
            price_per_unit = round(random.uniform(10, 500), 2)
            
            # Total shipment value
            total_value = quantity * price_per_unit
            
            records.append({
                "date": date.strftime("%Y-%m-%d"),
                "store_name": store,
                "product_name": product,
                "quantity": quantity,
                "price_per_unit": price_per_unit,
                "total_value": round(total_value, 2)
            })

# Create DataFrame
df = pd.DataFrame(records)

# Save to Excel
output_file = "data/shipments_data.xlsx"
df.to_excel(output_file, index=False, sheet_name="Shipments")

print(f"✓ Excel file created: {output_file}")
print(f"✓ Total records: {len(df)}")
print(f"✓ Date range: {df['date'].min()} to {df['date'].max()}")
print(f"✓ Stores: {df['store_name'].nunique()}")
print(f"✓ Products: {df['product_name'].nunique()}")
print(f"\nData sample:")
print(df.head(10))
print(f"\nAnomalies (negative or extremely high quantities):")
print(df[(df['quantity'] < 0) | (df['quantity'] > 200)])
