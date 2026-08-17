import pandas as pd
import mysql.connector
from getpass import getpass

# Connect to MySQL
password = getpass("MySQL password: ")

connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password=password,
    database="inventory_optimization"
)

print("Connected to MySQL successfully!")

# Load data from MySQL into Pandas
query = "SELECT * FROM orders_raw"

df = pd.read_sql(query, connection)

print("Data loaded successfully!")
print("Rows:", len(df))
print("Columns:", len(df.columns))

# Close connection
connection.close()

print("MySQL connection closed.")
# ==========================================
# PYTHON DATA EXPLORATION
# ==========================================

print("\nFirst 5 rows:")
print(df.head())

print("\nDataset shape:")
print(df.shape)

print("\nColumn names:")
print(df.columns.tolist())

print("\nData types:")
print(df.dtypes)

print("\nMissing values:")
print(df.isnull().sum())

print("\nBasic statistics:")
print(df.describe())
# ==========================================
# PYTHON DATA CLEANING
# ==========================================

# Convert date columns to datetime
df["order_date"] = pd.to_datetime(df["order_date"])
df["shipping_date"] = pd.to_datetime(df["shipping_date"])

# Check duplicate rows
print("\nDuplicate rows:")
print(df.duplicated().sum())

# Check negative values
print("\nNegative sales:")
print((df["sales"] < 0).sum())

print("\nNegative product prices:")
print((df["product_price"] < 0).sum())

print("\nNegative quantities:")
print((df["order_item_quantity"] < 0).sum())

# Create shipping delay
df["shipping_delay"] = (
    df["days_shipping_real"] - df["days_shipping_scheduled"]
)

print("\nShipping delay statistics:")
print(df["shipping_delay"].describe())
# ==========================================
# BUSINESS ANALYSIS
# ==========================================

# 1. Overall KPIs
total_orders = len(df)
total_sales = df["sales"].sum()
total_quantity = df["order_item_quantity"].sum()
avg_profit_ratio = df["profit_ratio"].mean()
risky_orders = df["late_delivery_risk"].sum()
risk_percentage = (risky_orders / total_orders) * 100

print("\n========== OVERALL KPIs ==========")
print("Total Orders:", total_orders)
print("Total Sales:", round(total_sales, 2))
print("Total Quantity Sold:", total_quantity)
print("Average Profit Ratio:", round(avg_profit_ratio, 2))
print("Risky Orders:", risky_orders)
print("Risk Percentage:", round(risk_percentage, 2), "%")
# ==========================================
# 2. PRODUCT PERFORMANCE ANALYSIS
# ==========================================

product_analysis = (
    df.groupby("product_name")
      .agg(
          total_orders=("order_id", "count"),
          total_quantity_sold=("order_item_quantity", "sum"),
          total_sales=("sales", "sum"),
          avg_profit_ratio=("profit_ratio", "mean"),
          risky_orders=("late_delivery_risk", "sum"),
          avg_shipping_delay=("shipping_delay", "mean")
      )
      .reset_index()
)

product_analysis["risk_percentage"] = (
    product_analysis["risky_orders"] /
    product_analysis["total_orders"] * 100
)

# Top 10 products by sales
top_products = product_analysis.sort_values(
    "total_sales",
    ascending=False
).head(10)

print("\n========== TOP 10 PRODUCTS BY SALES ==========")
print(top_products.to_string(index=False))
# 2. Customer Segment Analysis

segment_analysis = (
    df.groupby("customer_segment")
    .agg(
        total_orders=("order_id", "count"),
        total_quantity_sold=("order_item_quantity", "sum"),
        total_sales=("sales", "sum"),
        avg_profit_ratio=("profit_ratio", "mean"),
        risky_orders=("late_delivery_risk", "sum")
    )
    .reset_index()
)

segment_analysis["risk_percentage"] = (
    segment_analysis["risky_orders"] /
    segment_analysis["total_orders"] * 100
)

print("\n========== CUSTOMER SEGMENT ANALYSIS ==========")
print(segment_analysis.to_string(index=False))
# 3. Regional Analysis

region_analysis = (
    df.groupby("order_region")
    .agg(
        total_orders=("order_id", "count"),
        risky_orders=("late_delivery_risk", "sum"),
        avg_shipping_days=("days_shipping_real", "mean"),
        avg_scheduled_days=("days_shipping_scheduled", "mean")
    )
    .reset_index()
)

region_analysis["risk_percentage"] = (
    region_analysis["risky_orders"] /
    region_analysis["total_orders"] * 100
)

region_analysis = region_analysis.sort_values(
    "risk_percentage",
    ascending=False
)

print("\n========== REGIONAL DELIVERY RISK ==========")
print(region_analysis.to_string(index=False))
# 4. Delivery Risk Analysis

delivery_analysis = (
    df.groupby("late_delivery_risk")
    .agg(
        total_orders=("order_id", "count"),
        avg_actual_shipping_days=("days_shipping_real", "mean"),
        avg_scheduled_shipping_days=("days_shipping_scheduled", "mean"),
        avg_shipping_delay=("shipping_delay", "mean"),
        avg_profit_ratio=("profit_ratio", "mean"),
        total_sales=("sales", "sum")
    )
    .reset_index()
)

delivery_analysis["risk_status"] = delivery_analysis["late_delivery_risk"].map({
    0: "On Time",
    1: "Late Risk"
})

print("\n========== DELIVERY RISK ANALYSIS ==========")
print(delivery_analysis.to_string(index=False))
# 5. Export Analysis Results for Power BI

product_analysis.to_csv("product_analysis.csv", index=False)
segment_analysis.to_csv("segment_analysis.csv", index=False)
region_analysis.to_csv("region_analysis.csv", index=False)
delivery_analysis.to_csv("delivery_analysis.csv", index=False)

print("\n========== EXPORT COMPLETE ==========")
print("Analysis files saved successfully!")
# ==========================================
# 6. INVENTORY OPTIMIZATION ANALYSIS
# ==========================================

# ABC Classification
abc_analysis = (
    df.groupby("product_name")
    .agg(total_revenue=("sales", "sum"))
    .sort_values("total_revenue", ascending=False)
    .reset_index()
)

abc_analysis["cumulative_revenue"] = abc_analysis["total_revenue"].cumsum()
abc_analysis["cumulative_pct"] = (
    abc_analysis["cumulative_revenue"]
    / abc_analysis["total_revenue"].sum()
) * 100

abc_analysis["abc_class"] = abc_analysis["cumulative_pct"].apply(
    lambda x: "A" if x <= 80 else ("B" if x <= 95 else "C")
)


# Demand Variability
monthly_demand = (
    df.groupby(
        ["product_name", "category_name", df["order_date"].dt.to_period("M")]
    )
    .agg(
        units_sold=("order_item_quantity", "sum"),
        revenue=("sales", "sum")
    )
    .reset_index()
)

monthly_demand["order_month"] = (
    monthly_demand["order_date"].astype(str)
)

demand_variability = (
    monthly_demand.groupby("product_name")
    .agg(
        avg_monthly_demand=("units_sold", "mean"),
        demand_stddev=("units_sold", "std")
    )
    .reset_index()
)
monthly_demand.to_csv("monthly_demand.csv", index=False)
demand_variability["coefficient_of_variation"] = (
    demand_variability["demand_stddev"]
    / demand_variability["avg_monthly_demand"]
)

demand_variability = demand_variability.sort_values(
    "coefficient_of_variation",
    ascending=False
)


# Export for Power BI
abc_analysis.to_csv("abc_analysis.csv", index=False)
demand_variability.to_csv("demand_variability.csv", index=False)

print("\nInventory optimization files saved successfully!")
# ==========================================
# 7. INVENTORY PRIORITY ANALYSIS
# ==========================================

# Product-level delivery risk
product_risk = (
    df.groupby("product_name")
    .agg(
        total_orders=("order_id", "count"),
        risky_orders=("late_delivery_risk", "sum")
    )
    .reset_index()
)

product_risk["risk_percentage"] = (
    product_risk["risky_orders"] /
    product_risk["total_orders"] * 100
)

# Combine ABC + demand variability + delivery risk
inventory_priority = abc_analysis[
    ["product_name", "total_revenue", "abc_class"]
].merge(
    demand_variability[
        ["product_name", "avg_monthly_demand",
         "demand_stddev", "coefficient_of_variation"]
    ],
    on="product_name",
    how="left"
).merge(
    product_risk[
        ["product_name", "risk_percentage"]
    ],
    on="product_name",
    how="left"
)

# Assign inventory priority
def assign_priority(row):
    if (
        (row["abc_class"] == "A" and row["risk_percentage"] > 50)
        or row["coefficient_of_variation"] > 1
    ):
        return "High Priority"

    elif (
        row["abc_class"] == "B"
        or row["risk_percentage"] > 50
    ):
        return "Medium Priority"

    else:
        return "Low Priority"


inventory_priority["inventory_priority"] = (
    inventory_priority.apply(assign_priority, axis=1)
)

# Export for Power BI
inventory_priority.to_csv(
    "inventory_priority.csv",
    index=False
)

print("\n========== INVENTORY PRIORITY ==========")
print(
    inventory_priority[
        [
            "product_name",
            "total_revenue",
            "abc_class",
            "avg_monthly_demand",
            "coefficient_of_variation",
            "risk_percentage",
            "inventory_priority"
        ]
    ]
    .sort_values(
        ["inventory_priority", "total_revenue"],
        ascending=[True, False]
    )
    .head(20)
    .to_string(index=False)
)

print("\nInventory priority file saved successfully!")
# ==========================================
# 8. MONTHLY SHIPPING PERFORMANCE
# ==========================================

monthly_shipping = (
    df.groupby(df["order_date"].dt.to_period("M"))
    .agg(
        avg_actual_shipping_days=("days_shipping_real", "mean"),
        avg_scheduled_shipping_days=("days_shipping_scheduled", "mean"),
        avg_shipping_delay=("shipping_delay", "mean")
    )
    .reset_index()
)

monthly_shipping["order_month"] = (
    monthly_shipping["order_date"].astype(str)
)

monthly_shipping.to_csv(
    "monthly_shipping.csv",
    index=False
)

print("\nMonthly shipping file saved successfully!")
# ==========================================
# 9. ORDER STATUS ANALYSIS
# ==========================================

order_status_analysis = (
    df.groupby("order_status")
    .agg(
        total_orders=("order_id", "count"),
        total_sales=("sales", "sum")
    )
    .reset_index()
    .sort_values("total_orders", ascending=False)
)

order_status_analysis.to_csv(
    "order_status_analysis.csv",
    index=False
)

print("\nOrder status file saved successfully!")
