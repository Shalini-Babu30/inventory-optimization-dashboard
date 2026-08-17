                                                                                        sql/inventory_analysis.sql
USE inventory_optimization;
#1. DATA VALIDATION
-- Total number of records
SELECT COUNT(*) AS total_records
FROM orders_raw;
-- Check table structure
DESCRIBE orders_raw;
-- Check for missing values
SELECT
    SUM(order_id IS NULL) AS missing_order_id,
    SUM(order_date IS NULL) AS missing_order_date,
    SUM(shipping_date IS NULL) AS missing_shipping_date,
    SUM(product_name IS NULL) AS missing_product_name,
    SUM(category_name IS NULL) AS missing_category,
    SUM(order_item_quantity IS NULL) AS missing_quantity,
    SUM(product_price IS NULL) AS missing_price,
    SUM(sales IS NULL) AS missing_sales,
    SUM(profit_ratio IS NULL) AS missing_profit_ratio,
    SUM(days_shipping_real IS NULL) AS missing_shipping_real,
    SUM(days_shipping_scheduled IS NULL) AS missing_shipping_scheduled,
    SUM(late_delivery_risk IS NULL) AS missing_delivery_risk,
    SUM(order_status IS NULL) AS missing_status,
    SUM(order_region IS NULL) AS missing_region,
    SUM(customer_segment IS NULL) AS missing_segment
FROM orders_raw;
# 2. DATASET OVERVIEW
SELECT
    COUNT(DISTINCT product_name) AS total_products,
    COUNT(DISTINCT category_name) AS total_categories,
    COUNT(DISTINCT order_region) AS total_regions,
    COUNT(DISTINCT customer_segment) AS total_customer_segments
FROM orders_raw;
# 3. TOP PRODUCTS BY QUANTITY SOLD
SELECT
    product_name,
    SUM(order_item_quantity) AS total_quantity_sold,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(AVG(profit_ratio), 2) AS avg_profit_ratio
FROM orders_raw
GROUP BY product_name
ORDER BY total_quantity_sold DESC
LIMIT 10;
# 4. CATEGORY PERFORMANCE
SELECT
    category_name,
    SUM(order_item_quantity) AS total_quantity_sold,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(AVG(profit_ratio), 2) AS avg_profit_ratio
FROM orders_raw
GROUP BY category_name
ORDER BY total_sales DESC
LIMIT 10;
# 5. DELIVERY RISK OVERVIEW
SELECT
    late_delivery_risk,
    COUNT(*) AS total_orders,
    ROUND(AVG(days_shipping_real), 2) AS avg_actual_shipping_days,
    ROUND(AVG(days_shipping_scheduled), 2) AS avg_scheduled_shipping_days
FROM orders_raw
GROUP BY late_delivery_risk
ORDER BY late_delivery_risk DESC;
# 6. PRODUCTS WITH HIGHEST DELIVERY RISK
SELECT
    product_name,
    COUNT(*) AS total_orders,
    SUM(late_delivery_risk) AS risky_orders,
    ROUND(AVG(days_shipping_real), 2) AS avg_shipping_days
FROM orders_raw
GROUP BY product_name
ORDER BY risky_orders DESC
LIMIT 10;
# 7. REGIONAL DELIVERY RISK
SELECT
    order_region,
    COUNT(*) AS total_orders,
    SUM(late_delivery_risk) AS risky_orders,
    ROUND(SUM(late_delivery_risk) * 100.0 / COUNT(*), 2)
        AS risk_percentage,
    ROUND(AVG(days_shipping_real), 2) AS avg_shipping_days
FROM orders_raw
GROUP BY order_region
ORDER BY risk_percentage DESC;
# 8. CUSTOMER SEGMENT ANALYSIS
SELECT
    customer_segment,
    COUNT(*) AS total_orders,
    SUM(order_item_quantity) AS total_quantity_sold,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(AVG(profit_ratio), 2) AS avg_profit_ratio,
    SUM(late_delivery_risk) AS risky_orders,
    ROUND(SUM(late_delivery_risk) * 100.0 / COUNT(*), 2)
        AS risk_percentage
FROM orders_raw
GROUP BY customer_segment
ORDER BY total_sales DESC;
