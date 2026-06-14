import sys
from pathlib import Path
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from clean import load_and_clean
from analyse import (
    top_items_by_revenue, top_items_by_quantity,
    sales_by_hour, sales_by_day, monthly_revenue,
    revenue_by_category, server_performance, payment_split,
)

st.set_page_config(page_title="Restaurant Analytics", page_icon="🍽️", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
* { font-family: 'Inter', sans-serif !important; }

/* Background */
.stApp { background: #F0F4F8; }
#MainMenu, footer { visibility: hidden; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: #FFFFFF;
    border-right: 1px solid #E2E8F0;
}
[data-testid="stSidebar"] .stRadio label {
    font-size: 0.9rem !important;
    font-weight: 500 !important;
    color: #475569 !important;
    padding: 6px 0 !important;
}
[data-testid="stSidebar"] .stRadio [data-testid="stMarkdownContainer"] p {
    font-size: 0.9rem;
}

/* Metric cards */
[data-testid="metric-container"] {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 18px 20px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
[data-testid="stMetricLabel"] p {
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    color: #94A3B8 !important;
}
[data-testid="stMetricValue"] {
    font-size: 1.7rem !important;
    font-weight: 800 !important;
    color: #0F172A !important;
}

/* Charts inside white cards */
[data-testid="stPlotlyChart"] {
    background: #FFFFFF;
    border-radius: 12px;
    border: 1px solid #E2E8F0;
    padding: 16px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: #FFFFFF;
    border-radius: 10px;
    border: 1px solid #E2E8F0;
    padding: 4px;
    gap: 2px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    padding: 8px 20px;
    font-weight: 500;
    font-size: 0.875rem;
    color: #64748B;
    background: transparent;
    border: none;
}
.stTabs [aria-selected="true"] {
    background: #0EA5E9 !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
}

/* Section headings */
h3 { color: #0F172A !important; font-size: 1rem !important; font-weight: 700 !important; margin-bottom: 4px !important; }

/* Dataframe */
[data-testid="stDataFrame"] { border-radius: 10px; }

/* Multiselect tag */
[data-baseweb="tag"] { background: #EFF6FF !important; }
span[data-baseweb="tag"] span { color: #0EA5E9 !important; }

/* Radio dot colour */
[data-testid="stSidebar"] [data-baseweb="radio"] input:checked + div { background-color: #0EA5E9 !important; border-color: #0EA5E9 !important; }
</style>
""", unsafe_allow_html=True)

# ── Colours & helpers ─────────────────────────────────────────────────────────
BLUE  = "#0EA5E9"
CYAN  = "#06B6D4"
PAL   = [BLUE, CYAN, "#6366F1", "#F59E0B", "#10B981", "#EF4444", "#8B5CF6"]

def _layout(h=300):
    return dict(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter,sans-serif", color="#64748B", size=12),
        margin=dict(l=8, r=8, t=8, b=8), height=h,
        xaxis=dict(gridcolor="#F1F5F9", linecolor="#E2E8F0", zerolinecolor="#E2E8F0"),
        yaxis=dict(gridcolor="#F1F5F9", linecolor="#E2E8F0", zerolinecolor="#E2E8F0"),
        colorway=PAL, legend=dict(bgcolor="rgba(0,0,0,0)"),
    )

def show(fig, h=300):
    fig.update_layout(**_layout(h))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# ── Data ──────────────────────────────────────────────────────────────────────
df = load_and_clean()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🍽️ RestaurantIQ")
    st.caption("Sales Analytics · Jan 2024")
    st.divider()

    page = st.radio(
        "Navigation",
        ["📊 Dashboard", "🍕 Menu", "🕐 Time & Days", "👤 Staff", "📋 Raw Data"],
        label_visibility="collapsed",
    )

    st.divider()
    st.markdown("**Filters**")

    days = st.multiselect(
        "Day of week",
        ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],
        default=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],
    )
    cats = st.multiselect(
        "Category",
        sorted(df["category"].unique()),
        default=sorted(df["category"].unique()),
    )
    servers = st.multiselect(
        "Server",
        sorted(df["server"].unique()),
        default=sorted(df["server"].unique()),
    )

    st.divider()
    st.caption(f"📅 {len(df):,} total records")

filtered = df[
    df["day_of_week"].isin(days) &
    df["category"].isin(cats) &
    df["server"].isin(servers)
]

# ══════════════════════════════════════════════════════════════════════════════
# 📊 DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
if page == "📊 Dashboard":
    st.markdown("### Sales Overview")
    st.caption("All key metrics at a glance · January 2024")
    st.markdown("")

    # KPIs
    total_rev    = filtered["total_price"].sum()
    total_orders = filtered["order_id"].nunique()
    avg_val      = filtered["total_price"].mean() if len(filtered) else 0
    best_item    = top_items_by_quantity(filtered).iloc[0]["menu_item"] if len(filtered) else "—"
    top_server   = server_performance(filtered).iloc[0]["server"] if len(filtered) else "—"

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("💰 Revenue",       f"£{total_rev:,.0f}")
    k2.metric("🧾 Orders",        f"{total_orders:,}")
    k3.metric("📈 Avg Value",     f"£{avg_val:.2f}")
    k4.metric("🏆 Best Seller",   best_item)
    k5.metric("⭐ Top Server",    top_server)

    st.markdown("")

    # Row 1 — trend + category
    c1, c2 = st.columns([3, 2])

    with c1:
        st.markdown("### Daily Revenue Trend")
        daily = filtered.groupby("date")["total_price"].sum().reset_index()
        fig = go.Figure(go.Scatter(
            x=daily["date"], y=daily["total_price"],
            mode="lines+markers",
            line=dict(color=BLUE, width=2.5),
            marker=dict(size=7, color=BLUE, line=dict(color="white", width=2)),
            fill="tozeroy", fillcolor="rgba(14,165,233,0.07)",
            hovertemplate="<b>%{x|%b %d}</b><br>£%{y:,.2f}<extra></extra>",
        ))
        fig.update_yaxes(title="Revenue (£)")
        show(fig, 260)

    with c2:
        st.markdown("### Revenue by Category")
        data = revenue_by_category(filtered)
        fig = px.pie(data, values="revenue", names="category",
                     hole=0.55, color_discrete_sequence=PAL)
        fig.update_traces(textinfo="label+percent", textposition="outside",
                          hovertemplate="<b>%{label}</b><br>£%{value:,.0f}<extra></extra>")
        fig.update_layout(showlegend=False)
        show(fig, 260)

    # Row 2 — hours + days + payment
    c3, c4, c5 = st.columns(3)

    with c3:
        st.markdown("### Orders by Hour")
        data = sales_by_hour(filtered)
        fig = go.Figure(go.Bar(
            x=data["hour"], y=data["orders"],
            marker=dict(color=data["orders"],
                        colorscale=[[0,"#DBEAFE"],[1, BLUE]], line_width=0),
            hovertemplate="<b>%{x}:00</b><br>%{y} orders<extra></extra>",
        ))
        fig.update_xaxes(tickmode="linear", tick0=11, dtick=2)
        show(fig, 220)

    with c4:
        st.markdown("### Revenue by Day")
        data = sales_by_day(filtered)
        fig = px.bar(data, x="day_of_week", y="revenue",
                     color="revenue",
                     color_continuous_scale=[[0,"#DBEAFE"],[1,BLUE]],
                     labels={"day_of_week":"","revenue":"£"})
        fig.update_traces(marker_line_width=0)
        fig.update_layout(coloraxis_showscale=False)
        show(fig, 220)

    with c5:
        st.markdown("### Payment Split")
        data = payment_split(filtered)
        fig = px.pie(data, values="revenue", names="payment_method",
                     hole=0.55, color_discrete_sequence=[BLUE, CYAN])
        fig.update_traces(textinfo="label+percent", textposition="outside",
                          hovertemplate="<b>%{label}</b><br>£%{value:,.0f}<extra></extra>")
        fig.update_layout(showlegend=False)
        show(fig, 220)

# ══════════════════════════════════════════════════════════════════════════════
# 🍕 MENU
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🍕 Menu":
    st.markdown("### Menu Performance")
    st.caption("Which dishes drive the most revenue and orders")
    st.markdown("")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("### Top Items — Revenue")
        data = top_items_by_revenue(filtered)
        fig = px.bar(data, x="revenue", y="menu_item", orientation="h",
                     labels={"menu_item":"","revenue":"Revenue (£)"},
                     color="revenue",
                     color_continuous_scale=[[0,"#DBEAFE"],[1,BLUE]])
        fig.update_traces(marker_line_width=0)
        fig.update_layout(coloraxis_showscale=False, yaxis={"categoryorder":"total ascending"})
        show(fig, 360)

    with c2:
        st.markdown("### Top Items — Quantity Sold")
        data = top_items_by_quantity(filtered)
        fig = px.bar(data, x="quantity", y="menu_item", orientation="h",
                     labels={"menu_item":"","quantity":"Units sold"},
                     color="quantity",
                     color_continuous_scale=[[0,"#CFFAFE"],[1,CYAN]])
        fig.update_traces(marker_line_width=0)
        fig.update_layout(coloraxis_showscale=False, yaxis={"categoryorder":"total ascending"})
        show(fig, 360)

    st.markdown("### Category Breakdown")
    data = revenue_by_category(filtered)
    fig = px.bar(data, x="category", y="revenue", color="category",
                 color_discrete_sequence=PAL,
                 labels={"category":"","revenue":"Revenue (£)"},
                 text_auto=",.0f")
    fig.update_traces(marker_line_width=0, texttemplate="£%{text}", textposition="outside")
    fig.update_layout(showlegend=False, yaxis_range=[0, data["revenue"].max()*1.2])
    show(fig, 300)

# ══════════════════════════════════════════════════════════════════════════════
# 🕐 TIME & DAYS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🕐 Time & Days":
    st.markdown("### Time & Day Patterns")
    st.caption("When is the restaurant at its busiest?")
    st.markdown("")

    st.markdown("### Orders by Hour of Day")
    data = sales_by_hour(filtered)
    fig = go.Figure(go.Bar(
        x=data["hour"], y=data["orders"],
        marker=dict(color=data["orders"],
                    colorscale=[[0,"#DBEAFE"],[0.5,"#7DD3FC"],[1,BLUE]],
                    line_width=0),
        text=data["orders"], textposition="outside",
        hovertemplate="<b>%{x}:00</b><br>%{y} orders<extra></extra>",
    ))
    fig.update_xaxes(title="Hour", tickmode="linear", tick0=11, dtick=1)
    fig.update_yaxes(title="Orders")
    show(fig, 280)

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("### Revenue by Day of Week")
        data = sales_by_day(filtered)
        fig = px.bar(data, x="day_of_week", y="revenue",
                     color="revenue",
                     color_continuous_scale=[[0,"#DBEAFE"],[1,BLUE]],
                     labels={"day_of_week":"","revenue":"Revenue (£)"})
        fig.update_traces(marker_line_width=0)
        fig.update_layout(coloraxis_showscale=False)
        show(fig, 300)

    with c2:
        st.markdown("### Order Volume by Day")
        data = sales_by_day(filtered)
        fig = go.Figure(go.Scatter(
            x=list(data["day_of_week"]), y=data["orders"],
            mode="lines+markers",
            line=dict(color=CYAN, width=3),
            marker=dict(size=9, color=CYAN, line=dict(color="white", width=2)),
            fill="tozeroy", fillcolor="rgba(6,182,212,0.08)",
        ))
        fig.update_yaxes(title="Orders")
        show(fig, 300)

# ══════════════════════════════════════════════════════════════════════════════
# 👤 STAFF
# ══════════════════════════════════════════════════════════════════════════════
elif page == "👤 Staff":
    st.markdown("### Staff Performance")
    st.caption("Revenue and order count per server")
    st.markdown("")

    data = server_performance(filtered)
    cols = st.columns(len(data))
    for col, (_, row) in zip(cols, data.iterrows()):
        col.metric(f"👤 {row['server']}", f"£{row['revenue']:,.0f}", f"{int(row['orders'])} orders")

    st.markdown("")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("### Revenue per Server")
        fig = px.bar(data, x="server", y="revenue", color="server",
                     color_discrete_sequence=PAL,
                     labels={"server":"","revenue":"Revenue (£)"},
                     text_auto=",.0f")
        fig.update_traces(marker_line_width=0, texttemplate="£%{text}", textposition="outside")
        fig.update_layout(showlegend=False, yaxis_range=[0, data["revenue"].max()*1.2])
        show(fig, 320)

    with c2:
        st.markdown("### Orders per Server")
        fig = px.bar(data.sort_values("orders", ascending=False),
                     x="server", y="orders", color="server",
                     color_discrete_sequence=PAL,
                     labels={"server":"","orders":"Orders"})
        fig.update_traces(marker_line_width=0)
        fig.update_layout(showlegend=False)
        show(fig, 320)

    st.markdown("### Full Staff Table")
    display = data.copy()
    display["revenue"] = display["revenue"].map("£{:,.2f}".format)
    display.columns = ["Server", "Orders", "Revenue"]
    st.dataframe(display, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════════════
# 📋 RAW DATA
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📋 Raw Data":
    st.markdown("### Raw Transaction Data")
    st.caption(f"Showing {len(filtered):,} records with current filters applied")
    st.markdown("")
    st.dataframe(filtered.sort_values("date"), use_container_width=True, hide_index=True)
