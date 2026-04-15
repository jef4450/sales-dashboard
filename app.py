# ================================
# 1. IMPORTS
# ================================
import streamlit as st
import pandas as pd
import plotly.express as px

from sklearn.linear_model import LinearRegression
import numpy as np

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
# 🔥 ML DATA PREPARATION
# ================================
df = df.sort_values('Order Date')

daily_sales = df.groupby('Order Date')['Sales'].sum().reset_index()

daily_sales['Days'] = (daily_sales['Order Date'] - daily_sales['Order Date'].min()).dt.days

X = daily_sales[['Days']]
y = daily_sales['Sales']

model = LinearRegression()
model.fit(X, y)

# Future predictions (next 30 days)
last_day = X['Days'].max()
future_days = np.arange(last_day + 1, last_day + 31).reshape(-1, 1)
future_preds = model.predict(future_days)

future_dates = pd.date_range(
    start=daily_sales['Order Date'].max() + pd.Timedelta(days=1),
    periods=30
)

forecast_df = pd.DataFrame({
    'Order Date': future_dates,
    'Sales': future_preds
})

# ================================
# 4. SIDEBAR FILTERS
# ================================
st.sidebar.header("Filters")

region = st.sidebar.multiselect(
    "Select Region",
    options=df['Region'].unique(),
    default=df['Region'].unique()
)

category = st.sidebar.multiselect(
    "Select Category",
    options=df['Category'].unique(),
    default=df['Category'].unique()
)

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

# --- Sub-category ---
subcat_sales = filtered_df.groupby('Sub-Category')['Sales'].sum().reset_index()

fig5 = px.bar(
    subcat_sales,
    x='Sales',
    y='Sub-Category',
    orientation='h',
    title='Sales by Sub-Category'
)

# ================================
# 🔥 8. FORECAST CHART (IMPROVED)
# ================================

st.subheader("📈 Sales Forecast (Next 30 Days)")

# Actual data
actual_df = daily_sales.copy()
actual_df['Type'] = 'Actual'

# Forecast data
forecast_df_copy = forecast_df.copy()
forecast_df_copy['Type'] = 'Forecast'

# Combine
combined_df = pd.concat([actual_df, forecast_df_copy])

# Plot
fig6 = px.line(
    combined_df,
    x='Order Date',
    y='Sales',
    color='Type',
    title='Sales Forecast vs Actual',
)

# Make forecast dashed
fig6.update_traces(
    line=dict(dash='dash'),
    selector=dict(name='Forecast')
)

# ================================
# 9. DISPLAY CHARTS
# ================================

st.plotly_chart(fig1, use_container_width=True)
st.plotly_chart(fig2, use_container_width=True)
st.plotly_chart(fig3, use_container_width=True)
st.plotly_chart(fig4, use_container_width=True)
st.plotly_chart(fig5, use_container_width=True)

st.plotly_chart(fig6, use_container_width=True)
