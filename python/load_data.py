import pandas as pd
import pymysql
from getpass import getpass

# Read the CSV
df = pd.read_csv(
    "DataCoSupplyChainDataset.csv",
    encoding="latin1"
)

print("CSV loaded:", len(df), "rows")

# Ask for MySQL password without displaying it
password = getpass("MySQL password: ")

# Connect to MySQL
connection = pymysql.connect(
    host="localhost",
    user="root",
    password=password
)

cursor = connection.cursor()

# Create database
cursor.execute("CREATE DATABASE IF NOT EXISTS inventory_optimization")
cursor.execute("USE inventory_optimization")

# Create table
cursor.execute("""
CREATE TABLE IF NOT EXISTS orders_raw (
    order_id INT,
    order_date DATETIME,
    shipping_date DATETIME,
    product_name VARCHAR(255),
    category_name VARCHAR(255),
    order_item_quantity INT,
    product_price DECIMAL(12,2),
    sales DECIMAL(12,2),
    profit_ratio DECIMAL(10,4),
    days_shipping_real INT,
    days_shipping_scheduled INT,
    late_delivery_risk INT,
    order_status VARCHAR(50),
    order_region VARCHAR(100),
    customer_segment VARCHAR(100)
)
""")

connection.commit()

# Keep only the columns needed for our project
columns = [
    "Order Id",
    "order date (DateOrders)",
    "shipping date (DateOrders)",
    "Product Name",
    "Category Name",
    "Order Item Quantity",
    "Product Price",
    "Sales",
    "Order Profit Per Order",
    "Days for shipping (real)",
    "Days for shipment (scheduled)",
    "Late_delivery_risk",
    "Order Status",
    "Order Region",
    "Customer Segment"
]

df = df[columns]

# Rename columns
df.columns = [
    "order_id",
    "order_date",
    "shipping_date",
    "product_name",
    "category_name",
    "order_item_quantity",
    "product_price",
    "sales",
    "profit_ratio",
    "days_shipping_real",
    "days_shipping_scheduled",
    "late_delivery_risk",
    "order_status",
    "order_region",
    "customer_segment"
]

# Convert dates
df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
df["shipping_date"] = pd.to_datetime(df["shipping_date"], errors="coerce")

# Replace missing values
df = df.where(pd.notnull(df), None)

# Insert data in batches
insert_query = """
INSERT INTO orders_raw (
    order_id,
    order_date,
    shipping_date,
    product_name,
    category_name,
    order_item_quantity,
    product_price,
    sales,
    profit_ratio,
    days_shipping_real,
    days_shipping_scheduled,
    late_delivery_risk,
    order_status,
    order_region,
    customer_segment
)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

data = [tuple(row) for row in df.itertuples(index=False, name=None)]

batch_size = 5000

for i in range(0, len(data), batch_size):
    cursor.executemany(insert_query, data[i:i + batch_size])
    connection.commit()
    print(f"Loaded {min(i + batch_size, len(data))} / {len(data)} rows")

cursor.close()
connection.close()

print("DONE! Data loaded successfully.")