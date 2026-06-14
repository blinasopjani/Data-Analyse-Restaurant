import sys
from pathlib import Path
import streamlit as st
import plotly.express as px
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from clean import load_and_clean
from analyse import (
    top_items_by_revenue,
    top_items_by_quantity,
    sales_by_hour,
    sales_by_day,
    monthly_revenue,
    revenue_by_category,
    server_performance,
    payment_split,
)

st.set_page_config(page_title="Restaurant Sales Dashboard", layout="wide")
st.title("Restaurant Sales Dashboard")

df = load_and_clean()

# --- Sidebar filters ---
st.sidebar.header("Filters")
days = st.sidebar.multiselect(
    "Day of week",
    options=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
    default=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
)
categories = st.sidebar.multiselect(
    "Category",
    options=sorted(df["category"].unique()),
    default=sorted(df["category"].unique()),
)

filtered = df[df["day_of_week"].isin(days) & df["category"].isin(categories)]

# --- KPI row ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Revenue", f"£{filtered['total_price'].sum():,.2f}")
col2.metric("Total Orders", f"{filtered['order_id'].nunique():,}")
col3.metric("Avg Order Value", f"£{filtered['total_price'].mean():.2f}")
col4.metric("Best Selling Item", top_items_by_quantity(filtered).iloc[0]["menu_item"])

st.divider()

# --- Charts row 1 ---
c1, c2 = st.columns(2)

with c1:
    st.subheader("Top Items by Revenue")
    data = top_items_by_revenue(filtered)
    fig = px.bar(data, x="revenue", y="menu_item", orientation="h", color="revenue",
                 color_continuous_scale="Blues", labels={"menu_item": "", "revenue": "Revenue (£)"})
    fig.update_layout(coloraxis_showscale=False, yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.subheader("Revenue by Category")
    data = revenue_by_category(filtered)
    fig = px.pie(data, values="revenue", names="category", hole=0.4)
    st.plotly_chart(fig, use_container_width=True)

# --- Charts row 2 ---
c3, c4 = st.columns(2)

with c3:
    st.subheader("Busiest Hours")
    data = sales_by_hour(filtered)
    fig = px.bar(data, x="hour", y="orders", color="orders", color_continuous_scale="Oranges",
                 labels={"hour": "Hour of day", "orders": "Number of orders"})
    fig.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

with c4:
    st.subheader("Revenue by Day of Week")
    data = sales_by_day(filtered)
    fig = px.bar(data, x="day_of_week", y="revenue",
                 labels={"day_of_week": "", "revenue": "Revenue (£)"})
    st.plotly_chart(fig, use_container_width=True)

# --- Charts row 3 ---
c5, c6 = st.columns(2)

with c5:
    st.subheader("Monthly Revenue Trend")
    data = monthly_revenue(filtered)
    fig = px.line(data, x="month", y="revenue", markers=True,
                  labels={"month": "Month", "revenue": "Revenue (£)"})
    st.plotly_chart(fig, use_container_width=True)

with c6:
    st.subheader("Server Performance")
    data = server_performance(filtered)
    fig = px.bar(data, x="server", y="revenue", color="orders",
                 labels={"server": "Server", "revenue": "Revenue (£)", "orders": "Orders"})
    st.plotly_chart(fig, use_container_width=True)

# --- Payment split ---
st.subheader("Payment Method Split")
data = payment_split(filtered)
fig = px.pie(data, values="revenue", names="payment_method", hole=0.4)
st.plotly_chart(fig, use_container_width=True)

# --- Raw data ---
with st.expander("Raw data"):
    st.dataframe(filtered, use_container_width=True)
