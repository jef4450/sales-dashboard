# ================================
# 1. IMPORTS
# ================================
import streamlit as st
import pandas as pd
import plotly.express as px

# ================================
# 2. PAGE CONFIG
# ================================
st.set_page_config(page_title="Sales Dashboard", layout="wide")

st.title("📊 Superstore Sales Dashboard")

st.markdown("""
This interactive dashboard analyzes retail sales data across regions, categories, and products.

Use the filters on the left to explore trends, compare performance, and identify top-selling products.
""")

# ================================
# 3. LOAD DATA
# ================================
df = pd.read_csv('data/superstore.csv', encoding='latin1')

# Convert dates
df['Order Date'] = pd.to_datetime(df['Order Date'], dayfirst=True)

# Create Year/Month
df['Year'] = df['Order Date'].dt.year
df['Month'] = df['Order Date'].dt.month

# ================================
# 4. SIDEBAR FILTERS
# ================================
st.sidebar.header("Filters")

# Region filter
region = st.sidebar.multiselect(
    "Select Region",
    options=df['Region'].unique(),
    default=df['Region'].unique()
)

# Category filter
category = st.sidebar.multiselect(
    "Select Category",
    options=df['Category'].unique(),
    default=df['Category'].unique()
)

# Date range filter
date_range = st.sidebar.date_input(
    "Select Date Range",
    [df['Order Date'].min(), df['Order Date'].max()]
)

# ================================
# 5. APPLY FILTERS
# ================================
filtered_df = df[
    (df['Region'].isin(region)) &
    (df['Category'].isin(category)) &
    (df['Order Date'] >= pd.to_datetime(date_range[0])) &
    (df['Order Date'] <= pd.to_datetime(date_range[1]))
]

# ================================
# 6. KPIs
# ================================
total_sales = filtered_df['Sales'].sum()
order_count = filtered_df['Order ID'].nunique()

col1, col2 = st.columns(2)

col1.metric("💰 Total Sales", f"${total_sales:,.0f}")
col2.metric("📦 Total Orders", order_count)

# ================================
# 7. CHARTS
# ================================

# --- Sales by Region ---
sales_by_region = filtered_df.groupby('Region')['Sales'].sum().reset_index()

fig1 = px.bar(
    sales_by_region,
    x='Region',
    y='Sales',
    title='Sales by Region'
)

# --- Monthly Trend ---
monthly_sales = filtered_df.groupby(['Year', 'Month'])['Sales'].sum().reset_index()

fig2 = px.line(
    monthly_sales,
    x='Month',
    y='Sales',
    color='Year',
    title='Monthly Sales Trend'
)

# --- Category Pie ---
sales_by_category = filtered_df.groupby('Category')['Sales'].sum().reset_index()

fig3 = px.pie(
    sales_by_category,
    names='Category',
    values='Sales',
    title='Sales by Category'
)

# --- Top Products ---
top_products = filtered_df.groupby('Product Name')['Sales'].sum().reset_index()
top_products = top_products.sort_values(by='Sales', ascending=False).head(10)

fig4 = px.bar(
    top_products,
    x='Sales',
    y='Product Name',
    orientation='h',
    title='Top 10 Products'
)

# --- Sub-category (replacement chart) ---
subcat_sales = filtered_df.groupby('Sub-Category')['Sales'].sum().reset_index()

fig5 = px.bar(
    subcat_sales,
    x='Sales',
    y='Sub-Category',
    orientation='h',
    title='Sales by Sub-Category'
)

# ================================
# 8. DISPLAY CHARTS
# ================================

st.plotly_chart(fig1, use_container_width=True)
st.plotly_chart(fig2, use_container_width=True)
st.plotly_chart(fig3, use_container_width=True)
st.plotly_chart(fig4, use_container_width=True)
st.plotly_chart(fig5, use_container_width=True)
