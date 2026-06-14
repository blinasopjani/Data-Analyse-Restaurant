import sys
from pathlib import Path
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

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

st.set_page_config(
    page_title="Restaurant Analytics",
    page_icon="🍽️",
    layout="wide",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }

.stApp { background-color: #F8F9FC; }

/* Hide Streamlit branding */
#MainMenu, footer { visibility: hidden; }

/* Tabs styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 2px;
    background: #FFFFFF;
    padding: 6px;
    border-radius: 12px;
    border: 1px solid #E5E7EB;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    padding: 10px 22px;
    font-size: 0.875rem;
    font-weight: 500;
    color: #6B7280;
    background: transparent;
    border: none;
}
.stTabs [aria-selected="true"] {
    background: #4F6EF7 !important;
    color: white !important;
    font-weight: 600;
}

/* Metric cards */
[data-testid="metric-container"] {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 14px;
    padding: 16px 20px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
[data-testid="metric-container"] label {
    color: #9CA3AF !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #111827 !important;
    font-size: 1.7rem !important;
    font-weight: 800 !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #FFFFFF;
    border-right: 1px solid #E5E7EB;
}

/* Multiselect tags */
[data-baseweb="tag"] {
    background-color: #EEF2FF !important;
    color: #4F6EF7 !important;
}

/* Expander */
.streamlit-expanderHeader {
    background: #FFFFFF;
    border-radius: 10px;
    border: 1px solid #E5E7EB;
    font-weight: 600;
    color: #374151;
}
</style>
""", unsafe_allow_html=True)

# ── Plotly theme ──────────────────────────────────────────────────────────────
BLUE   = "#4F6EF7"
GREEN  = "#10B981"
ORANGE = "#F59E0B"
PURPLE = "#8B5CF6"
RED    = "#EF4444"
TEAL   = "#06B6D4"
PALETTE = [BLUE, GREEN, ORANGE, PURPLE, RED, TEAL, "#EC4899"]

def plot(fig, height=320):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#374151", size=12),
        margin=dict(l=10, r=10, t=10, b=10),
        height=height,
        xaxis=dict(gridcolor="#F3F4F6", linecolor="#E5E7EB", zerolinecolor="#E5E7EB"),
        yaxis=dict(gridcolor="#F3F4F6", linecolor="#E5E7EB", zerolinecolor="#E5E7EB"),
        legend=dict(bgcolor="rgba(0,0,0,0)", orientation="h", yanchor="bottom", y=1.02),
        colorway=PALETTE,
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# ── Data & sidebar filters ────────────────────────────────────────────────────
df = load_and_clean()

with st.sidebar:
    st.markdown("## 🍽️ RestaurantIQ")
    st.markdown("---")
    st.markdown("#### Filters")
    days = st.multiselect(
        "Day of week",
        ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],
        default=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],
    )
    categories = st.multiselect(
        "Category",
        sorted(df["category"].unique()),
        default=sorted(df["category"].unique()),
    )
    servers = st.multiselect(
        "Server",
        sorted(df["server"].unique()),
        default=sorted(df["server"].unique()),
    )
    st.markdown("---")
    st.caption(f"📅 Jan 2024 · {len(df):,} records")

filtered = df[
    df["day_of_week"].isin(days) &
    df["category"].isin(categories) &
    df["server"].isin(servers)
]

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("# 🍽️ Restaurant Analytics")
st.caption("Sales performance dashboard · January 2024")
st.markdown("")

# ── Tabs navigation ───────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "🍕 Menu", "🕐 Time & Days", "👤 Staff"])

# ═════════════════════════════════════════════════════════════════════════════
# TAB 1 — OVERVIEW
# ═════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown("")

    total_rev    = filtered["total_price"].sum()
    total_orders = filtered["order_id"].nunique()
    avg_order    = filtered["total_price"].mean() if len(filtered) else 0
    best_item    = top_items_by_quantity(filtered).iloc[0]["menu_item"] if len(filtered) else "—"

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("💰 Total Revenue",    f"£{total_rev:,.2f}")
    c2.metric("🧾 Total Orders",     f"{total_orders:,}")
    c3.metric("📈 Avg Order Value",  f"£{avg_order:.2f}")
    c4.metric("🏆 Best Seller",      best_item)

    st.markdown("---")

    # Revenue by category
    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown("##### Revenue by Category")
        data = revenue_by_category(filtered)
        fig = px.bar(
            data, x="category", y="revenue",
            labels={"category": "", "revenue": "Revenue (£)"},
            color="category", color_discrete_sequence=PALETTE,
            text_auto=",.0f",
        )
        fig.update_traces(marker_line_width=0, texttemplate="£%{text}", textposition="outside")
        fig.update_layout(showlegend=False, yaxis_range=[0, data["revenue"].max() * 1.18])
        plot(fig, 300)

    with col2:
        st.markdown("##### Payment Method")
        data = payment_split(filtered)
        fig = px.pie(
            data, values="revenue", names="payment_method", hole=0.58,
            color_discrete_sequence=[BLUE, ORANGE],
        )
        fig.update_traces(
            textposition="outside", textinfo="label+percent",
            hovertemplate="<b>%{label}</b><br>£%{value:,.2f}<extra></extra>",
        )
        fig.update_layout(showlegend=False)
        plot(fig, 300)

    # Monthly trend
    st.markdown("##### Monthly Revenue Trend")
    data = monthly_revenue(filtered)
    fig = go.Figure(go.Scatter(
        x=data["month"], y=data["revenue"],
        mode="lines+markers",
        line=dict(color=BLUE, width=3),
        marker=dict(size=10, color=BLUE, line=dict(color="white", width=2)),
        fill="tozeroy", fillcolor="rgba(79,110,247,0.06)",
        hovertemplate="<b>%{x}</b><br>£%{y:,.2f}<extra></extra>",
    ))
    fig.update_yaxes(title="Revenue (£)")
    plot(fig, 220)

# ═════════════════════════════════════════════════════════════════════════════
# TAB 2 — MENU
# ═════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("##### Top Items by Revenue")
        data = top_items_by_revenue(filtered)
        fig = px.bar(
            data, x="revenue", y="menu_item", orientation="h",
            labels={"menu_item": "", "revenue": "Revenue (£)"},
            color="revenue",
            color_continuous_scale=[[0, "#DBEAFE"], [1, BLUE]],
        )
        fig.update_traces(marker_line_width=0)
        fig.update_layout(
            coloraxis_showscale=False,
            yaxis={"categoryorder": "total ascending"},
        )
        plot(fig, 360)

    with col2:
        st.markdown("##### Top Items by Quantity Sold")
        data = top_items_by_quantity(filtered)
        fig = px.bar(
            data, x="quantity", y="menu_item", orientation="h",
            labels={"menu_item": "", "quantity": "Units sold"},
            color="quantity",
            color_continuous_scale=[[0, "#D1FAE5"], [1, GREEN]],
        )
        fig.update_traces(marker_line_width=0)
        fig.update_layout(
            coloraxis_showscale=False,
            yaxis={"categoryorder": "total ascending"},
        )
        plot(fig, 360)

    st.markdown("##### Category Comparison — Revenue vs Quantity")
    rev  = revenue_by_category(filtered).rename(columns={"revenue": "Revenue (£)"})
    qty  = top_items_by_quantity(filtered)
    cat  = filtered.groupby("category")["quantity"].sum().reset_index()
    merged = rev.merge(cat, on="category")
    fig = px.scatter(
        merged, x="Revenue (£)", y="quantity",
        size="Revenue (£)", color="category",
        labels={"quantity": "Units sold", "category": "Category"},
        color_discrete_sequence=PALETTE,
        size_max=50, hover_name="category",
    )
    plot(fig, 300)

# ═════════════════════════════════════════════════════════════════════════════
# TAB 3 — TIME & DAYS
# ═════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("")

    st.markdown("##### Orders by Hour of Day")
    data = sales_by_hour(filtered)
    fig = go.Figure(go.Bar(
        x=data["hour"], y=data["orders"],
        marker=dict(
            color=data["orders"],
            colorscale=[[0, "#DBEAFE"], [0.5, "#93C5FD"], [1, BLUE]],
            line_width=0,
        ),
        text=data["orders"],
        textposition="outside",
        hovertemplate="<b>%{x}:00</b><br>%{y} orders<extra></extra>",
    ))
    fig.update_xaxes(title="Hour", tickmode="linear", tick0=11, dtick=1)
    fig.update_yaxes(title="Orders")
    plot(fig, 270)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("##### Revenue by Day of Week")
        data = sales_by_day(filtered)
        fig = px.bar(
            data, x="day_of_week", y="revenue",
            labels={"day_of_week": "", "revenue": "Revenue (£)"},
            color="revenue",
            color_continuous_scale=[[0, "#FEF3C7"], [1, ORANGE]],
        )
        fig.update_traces(marker_line_width=0)
        fig.update_layout(coloraxis_showscale=False)
        plot(fig, 300)

    with col2:
        st.markdown("##### Order Volume by Day")
        data = sales_by_day(filtered)
        fig = px.line(
            data, x="day_of_week", y="orders",
            labels={"day_of_week": "", "orders": "Orders"},
            markers=True,
        )
        fig.update_traces(
            line=dict(color=ORANGE, width=3),
            marker=dict(size=10, color=ORANGE, line=dict(color="white", width=2)),
            fill="tozeroy", fillcolor="rgba(245,158,11,0.07)",
        )
        plot(fig, 300)

# ═════════════════════════════════════════════════════════════════════════════
# TAB 4 — STAFF
# ═════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("")

    data = server_performance(filtered)

    # Per-server metrics
    cols = st.columns(len(data))
    for col, (_, row) in zip(cols, data.iterrows()):
        col.metric(f"👤 {row['server']}", f"£{row['revenue']:,.0f}", f"{int(row['orders'])} orders")

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("##### Revenue per Server")
        fig = px.bar(
            data, x="server", y="revenue",
            labels={"server": "", "revenue": "Revenue (£)"},
            color="server", color_discrete_sequence=PALETTE,
            text_auto=",.0f",
        )
        fig.update_traces(marker_line_width=0, texttemplate="£%{text}", textposition="outside")
        fig.update_layout(showlegend=False, yaxis_range=[0, data["revenue"].max() * 1.18])
        plot(fig, 300)

    with col2:
        st.markdown("##### Orders per Server")
        fig = px.bar(
            data.sort_values("orders", ascending=False),
            x="server", y="orders",
            labels={"server": "", "orders": "Orders"},
            color="server", color_discrete_sequence=PALETTE,
        )
        fig.update_traces(marker_line_width=0)
        fig.update_layout(showlegend=False)
        plot(fig, 300)

    st.markdown("##### Full Staff Table")
    display = data.copy()
    display["revenue"] = display["revenue"].map("£{:,.2f}".format)
    display.columns = ["Server", "Orders", "Revenue"]
    st.dataframe(display, use_container_width=True, hide_index=True)
