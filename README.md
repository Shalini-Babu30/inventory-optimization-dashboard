# Inventory Optimization Dashboard
# Business Problem
Most retail analytics answers "what sold." This project answers the harder question: which products are at risk of stockout or overstock, and specifically how many units should trigger a reorder for each one.
Using approximately 180K order records, the goal was to move beyond descriptive reporting into actionable inventory planning by creating a prioritized list of products with calculated reorder points.
# Tools Used
SQL (MySQL) — data loading, cleaning, ABC classification via window functions, monthly demand aggregation
Python (pandas) — demand variability calculations, delivery risk analysis, inventory priority scoring
Excel — safety stock and reorder point formulas, conditional formatting, pivot summary
Power BI — 3-page interactive dashboard with DAX measures and data modeling
# Analysis Performed
Data cleaning — loaded ~180K order line items, checked for duplicates and nulls, calculated shipping delay (actual vs. scheduled shipping days).
ABC classification — ranked all 118 products by cumulative revenue share using a SQL window function, splitting them into Class A (top 80% of revenue), B (next 15%), and C (remaining 5%).
Demand variability — calculated average monthly demand, standard deviation, and coefficient of variation per product to identify which products have unpredictable (vs. steady) demand patterns.
Delivery risk analysis — measured late delivery risk by product, region, and customer segment.
Inventory priority scoring — combined ABC class, demand variability, and delivery risk into a single priority tier (High/Medium/Low) per product.
Reorder point calculation — in Excel, calculated Safety Stock (using a 95% service level, Z=1.65) and Reorder Point per product, based on a 14-day lead time assumption (stated explicitly since the raw dataset doesn't include real supplier lead times).
Dashboard build — modeled the data in Power BI across three pages: Inventory Overview, Inventory Optimization, and Demand & Supply Analysis.
# Inventory Optimization Method
Lead Time
A lead time of 14 days was assumed because the dataset does not contain actual supplier lead-time information.
Lead time assumed at 14 days based on average real-world supplier cycles, since the dataset doesn't include actual lead time data.
Safety Stock
Safety Stock was calculated using:
Safety Stock = 1.65 × Demand Standard Deviation × √(Lead Time / 30)
A Z-score of 1.65 was used to represent an approximately 95% service level.
Reorder Point
Reorder Point was calculated as:
Reorder Point = (Average Monthly Demand / 30 × Lead Time) + Safety Stock
This converts monthly demand into an estimated daily demand, accounts for demand during the lead-time period, and adds a safety buffer.
# Insights Generated
7 of 118 products (Class A) drive 80% of total revenue — the clear priority group for tight inventory control.
9 products flagged High Priority — either Class A with elevated delivery risk, or demand volatility (coefficient of variation) above 1, meaning month-to-month demand swings wider than the product's own average.
~55% of all orders carry late delivery risk, and it's nearly identical across Consumer, Corporate, and Home Office segments — pointing to a systemic fulfillment issue rather than a segment-specific one.
Concrete reorder numbers, not just flags — e.g., the highest-revenue product (~$6.9M in sales) has a calculated reorder point of ~339 units given the lead time assumption, giving a specific number to act on rather than a vague "watch this" label.
# Dashboard Preview
1. Inventory Overview
This page provides a high-level view of overall inventory and supply-chain performance, including total orders, sales, quantity sold, profit ratio, risky orders, product sales, customer segments, and delivery risk.
![Inventory Overview](screenshots/inventory_overview.png)
2. Inventory Optimization
This page focuses on ABC classification, demand variability, inventory priority, and product-level inventory risk.
![Inventory Optimization](screenshots/Inventory%20Optimization.png)
3. Demand & Supply Analysis
This page analyzes demand trends, units sold, shipping performance, shipping delays, and order-status distribution over time.
![Demand & Supply Analysis](screenshots/Demand%20%26%20Supply%20Analysis.png)
Excel Inventory Model
The Excel model converts the analytical results into actionable inventory planning metrics.
1.Safety Stock & Reorder Point
Safety stock was calculated using a 95% service-level assumption, followed by product-level reorder point calculations using the assumed 14-day lead time.
![Safety Stock & Reorder Point](screenshots/Safety%20Stock%20%26%20Reorder%20Point.png)
Inventory Priority Summary
2.A PivotTable summarizes the number of products, total reorder points, and average demand variability across inventory-priority categories.
![Inventory Priority Summary](screenshots/Inventory%20Priority%20Summary.png)
Excel Deliverable:** `inventory_calc_master.xlsx`
# Data Source
**DataCo Smart Supply Chain for Big Data Analysis** — Kaggle
[Dataset Link](https://www.kaggle.com/datasets/shashwatwork/dataco-smart-supply-chain-for-big-data-analysis)
The raw dataset is not included in this repository due to file size. The SQL analysis script used for data validation and transformation is available in:
`sql/inventory_analysis.sql`
# Business Impact
The analysis moves from descriptive reporting toward actionable inventory planning by identifying:
- Which products contribute the most revenue
- Which products have unpredictable demand
- Which products have higher delivery risk
- Which products require greater inventory attention
- When products should trigger replenishment based on calculated reorder points
The resulting workflow connects:
**Data → Analysis → Inventory Metrics → Prioritization → Business Decision**
