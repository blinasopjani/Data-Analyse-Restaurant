import sys
from pathlib import Path
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
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

st.set_page_config(
    page_title="Restaurant Analytics",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

  * { font-family: 'Inter', sans-serif !important; }

  .stApp { background: #F7F8FC; }

  /* hide default streamlit chrome */
  #MainMenu, footer, header { visibility: hidden; }
  [data-testid="collapsedControl"] { display: none; }
  .block-container { padding: 0 !important; max-width: 100% !important; }

  /* ── TOP NAVBAR ── */
  .navbar {
    background: #ffffff;
    border-bottom: 1px solid #E8EAF0;
    padding: 0 40px;
    display: flex;
    align-items: center;
    height: 64px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    position: sticky;
    top: 0;
    z-index: 999;
  }
  .navbar-brand {
    font-size: 1.15rem;
    font-weight: 800;
    color: #1A1A2E;
    display: flex;
    align-items: center;
    gap: 8px;
    margin-right: 40px;
    white-space: nowrap;
  }
  .navbar-brand span { color: #4F6EF7; }
  .navbar-links {
    display: flex;
    gap: 4px;
    flex: 1;
  }
  .nav-link {
    padding: 8px 18px;
    border-radius: 8px;
    font-size: 0.875rem;
    font-weight: 500;
    color: #6B7280;
    cursor: pointer;
    text-decoration: none;
    transition: all .15s;
    border: none;
    background: transparent;
  }
  .nav-link:hover { background: #F3F4F6; color: #1A1A2E; }
  .nav-link.active { background: #EEF2FF; color: #4F6EF7; font-weight: 600; }
  .navbar-badge {
    margin-left: auto;
    background: #F0FDF4;
    color: #16A34A;
    border: 1px solid #BBF7D0;
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 0.75rem;
    font-weight: 600;
  }

  /* ── PAGE BODY ── */
  .page-body { padding: 32px 40px; }

  /* ── PAGE TITLE ── */
  .page-title {
    font-size: 1.6rem;
    font-weight: 800;
    color: #1A1A2E;
    margin-bottom: 4px;
  }
  .page-subtitle {
    font-size: 0.875rem;
    color: #9CA3AF;
    margin-bottom: 28px;
  }

  /* ── FILTERS BAR ── */
  .filter-bar {
    background: #ffffff;
    border: 1px solid #E8EAF0;
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 24px;
    display: flex;
    gap: 16px;
    align-items: center;
  }
  .filter-label {
    font-size: 0.78rem;
    font-weight: 600;
    color: #6B7280;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    white-space: nowrap;
  }

  /* ── KPI CARDS ── */
  .kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 24px;
  }
  .kpi-card {
    background: #ffffff;
    border: 1px solid #E8EAF0;
    border-radius: 14px;
    padding: 20px 24px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
  }
  .kpi-card-top {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 12px;
  }
  .kpi-icon {
    width: 40px;
    height: 40px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.1rem;
  }
  .kpi-label {
    font-size: 0.78rem;
    font-weight: 600;
    color: #9CA3AF;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 6px;
  }
  .kpi-value {
    font-size: 1.9rem;
    font-weight: 800;
    color: #1A1A2E;
    line-height: 1;
    margin-bottom: 8px;
  }
  .kpi-sub {
    font-size: 0.78rem;
    color: #9CA3AF;
  }
  .kpi-sub b { color: #16A34A; }

  /* ── CHART CARDS ── */
  .chart-card {
    background: #ffffff;
    border: 1px solid #E8EAF0;
    border-radius: 14px;
    padding: 20px 24px 8px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    margin-bottom: 20px;
  }
  .chart-title {
    font-size: 0.95rem;
    font-weight: 700;
    color: #1A1A2E;
    margin-bottom: 2px;
  }
  .chart-sub {
    font-size: 0.78rem;
    color: #9CA3AF;
    margin-bottom: 12px;
  }

  /* ── TABLE ── */
  .table-card {
    background: #ffffff;
    border: 1px solid #E8EAF0;
    border-radius: 14px;
    padding: 20px 24px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
  }

  /* ── Streamlit widget tweaks ── */
  .stMultiSelect [data-baseweb="tag"] { background: #EEF2FF !important; }
  .stTabs [data-baseweb="tab-list"] { display: none; }
  div[data-testid="stHorizontalBlock"] { gap: 16px; }
  .stDataFrame { border-radius: 10px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Load data ─────────────────────────────────────────────────────────────────
df = load_and_clean()

# ── Session state for nav ─────────────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "Overview"

PAGES = ["Overview", "Menu", "Time & Days", "Staff"]

# ── Navbar ────────────────────────────────────────────────────────────────────
st.markdown('<div class="navbar"><div class="navbar-brand">🍽️ Restaurant<span>IQ</span></div><div class="navbar-links">', unsafe_allow_html=True)

cols = st.columns([1.2] + [0.7] * len(PAGES) + [2])
for i, page in enumerate(PAGES):
    with cols[i + 1]:
        active = "active" if st.session_state.page == page else ""
        if st.button(page, key=f"nav_{page}", use_container_width=True):
            st.session_state.page = page
            st.rerun()

with cols[-1]:
    st.markdown(f'<div style="text-align:right;padding-top:4px"><span style="background:#F0FDF4;color:#16A34A;border:1px solid #BBF7D0;border-radius:20px;padding:4px 14px;font-size:0.75rem;font-weight:600">● Live · Jan 2024</span></div>', unsafe_allow_html=True)

st.markdown('</div></div>', unsafe_allow_html=True)

# ── Plotly shared theme ───────────────────────────────────────────────────────
BLUE    = "#4F6EF7"
GREEN   = "#10B981"
ORANGE  = "#F59E0B"
RED     = "#EF4444"
PURPLE  = "#8B5CF6"
PALETTE = [BLUE, GREEN, ORANGE, RED, PURPLE, "#06B6D4", "#EC4899"]

def base_layout(height=320):
    return dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#374151", size=12),
        margin=dict(l=8, r=8, t=8, b=8),
        height=height,
        xaxis=dict(gridcolor="#F3F4F6", linecolor="#E5E7EB", zerolinecolor="#E5E7EB"),
        yaxis=dict(gridcolor="#F3F4F6", linecolor="#E5E7EB", zerolinecolor="#E5E7EB"),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        colorway=PALETTE,
    )

def show_chart(fig, height=320):
    fig.update_layout(**base_layout(height))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

def card_start(title, subtitle=""):
    st.markdown(f'<div class="chart-card"><div class="chart-title">{title}</div><div class="chart-sub">{subtitle}</div>', unsafe_allow_html=True)

def card_end():
    st.markdown('</div>', unsafe_allow_html=True)

# ── Sidebar filters (shared) ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Filters")
    days = st.multiselect("Day of week", ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],
                          default=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"])
    categories = st.multiselect("Category", sorted(df["category"].unique()), default=sorted(df["category"].unique()))

filtered = df[df["day_of_week"].isin(days) & df["category"].isin(categories)]

# ─────────────────────────────────────────────────────────────────────────────
# PAGE: OVERVIEW
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state.page == "Overview":
    st.markdown('<div class="page-body">', unsafe_allow_html=True)
    st.markdown('<div class="page-title">Sales Overview</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">All key metrics at a glance · January 2024</div>', unsafe_allow_html=True)

    # KPIs
    total_rev    = filtered["total_price"].sum()
    total_orders = filtered["order_id"].nunique()
    avg_order    = filtered["total_price"].mean() if len(filtered) else 0
    best_item    = top_items_by_quantity(filtered).iloc[0]["menu_item"] if len(filtered) else "—"

    k1, k2, k3, k4 = st.columns(4)

    for col, icon, bg, label, value, sub in [
        (k1, "💰", "#EEF2FF", "Total Revenue",   f"£{total_rev:,.0f}",     "January 2024"),
        (k2, "🧾", "#F0FDF4", "Total Orders",    f"{total_orders:,}",       "Unique orders"),
        (k3, "📊", "#FFF7ED", "Avg Order Value", f"£{avg_order:.2f}",       "Per transaction"),
        (k4, "🏆", "#FDF4FF", "Best Seller",     best_item,                 "Most ordered item"),
    ]:
        with col:
            st.markdown(f"""
            <div class="kpi-card">
              <div style="font-size:1.6rem;margin-bottom:10px">{icon}</div>
              <div class="kpi-label">{label}</div>
              <div class="kpi-value" style="font-size:{'1.5rem' if len(str(value))>8 else '1.9rem'}">{value}</div>
              <div class="kpi-sub">{sub}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # Row 1
    c1, c2 = st.columns([3, 2])
    with c1:
        card_start("Revenue by Category", "Breakdown of total sales per food category")
        data = revenue_by_category(filtered)
        fig = px.bar(data, x="category", y="revenue",
                     labels={"category": "", "revenue": "Revenue (£)"},
                     color="category", color_discrete_sequence=PALETTE)
        fig.update_traces(marker_line_width=0)
        fig.update_layout(showlegend=False)
        show_chart(fig, 280)
        card_end()

    with c2:
        card_start("Payment Split", "Card vs cash share of revenue")
        data = payment_split(filtered)
        fig = px.pie(data, values="revenue", names="payment_method", hole=0.6,
                     color_discrete_sequence=[BLUE, ORANGE])
        fig.update_traces(textposition="outside", textinfo="label+percent",
                          hovertemplate="<b>%{label}</b><br>£%{value:,.2f}<extra></extra>")
        fig.update_layout(showlegend=False)
        show_chart(fig, 280)
        card_end()

    # Row 2 — monthly trend full width
    card_start("Monthly Revenue Trend", "How revenue has evolved month over month")
    data = monthly_revenue(filtered)
    fig = go.Figure(go.Scatter(
        x=data["month"], y=data["revenue"],
        mode="lines+markers",
        line=dict(color=BLUE, width=3),
        marker=dict(size=9, color=BLUE, line=dict(color="white", width=2)),
        fill="tozeroy", fillcolor="rgba(79,110,247,0.07)",
        hovertemplate="<b>%{x}</b><br>£%{y:,.2f}<extra></extra>",
    ))
    fig.update_yaxes(title="Revenue (£)")
    show_chart(fig, 240)
    card_end()

    st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# PAGE: MENU
# ─────────────────────────────────────────────────────────────────────────────
elif st.session_state.page == "Menu":
    st.markdown('<div class="page-body">', unsafe_allow_html=True)
    st.markdown('<div class="page-title">Menu Performance</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Which dishes drive the most revenue and orders</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        card_start("Top Items by Revenue", "Total £ generated per menu item")
        data = top_items_by_revenue(filtered)
        fig = px.bar(data, x="revenue", y="menu_item", orientation="h",
                     labels={"menu_item": "", "revenue": "Revenue (£)"},
                     color="revenue", color_continuous_scale=[[0,"#DBEAFE"],[1, BLUE]])
        fig.update_traces(marker_line_width=0)
        fig.update_layout(coloraxis_showscale=False, yaxis={"categoryorder":"total ascending"})
        show_chart(fig, 340)
        card_end()

    with c2:
        card_start("Top Items by Quantity", "Number of units sold per item")
        data = top_items_by_quantity(filtered)
        fig = px.bar(data, x="quantity", y="menu_item", orientation="h",
                     labels={"menu_item": "", "quantity": "Units sold"},
                     color="quantity", color_continuous_scale=[[0,"#D1FAE5"],[1, GREEN]])
        fig.update_traces(marker_line_width=0)
        fig.update_layout(coloraxis_showscale=False, yaxis={"categoryorder":"total ascending"})
        show_chart(fig, 340)
        card_end()

    card_start("Category Revenue Breakdown", "Revenue and order count per food category")
    data = revenue_by_category(filtered)
    fig = px.bar(data, x="category", y="revenue",
                 labels={"category": "", "revenue": "Revenue (£)"},
                 color="category", color_discrete_sequence=PALETTE, text_auto=".0f")
    fig.update_traces(marker_line_width=0, textposition="outside",
                      texttemplate="£%{text}")
    fig.update_layout(showlegend=False, yaxis_range=[0, data["revenue"].max() * 1.15])
    show_chart(fig, 300)
    card_end()

    st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# PAGE: TIME & DAYS
# ─────────────────────────────────────────────────────────────────────────────
elif st.session_state.page == "Time & Days":
    st.markdown('<div class="page-body">', unsafe_allow_html=True)
    st.markdown('<div class="page-title">Time & Day Patterns</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">When is the restaurant at its busiest?</div>', unsafe_allow_html=True)

    # Hour heatmap-style bar
    card_start("Orders by Hour", "Volume of orders across each hour of the day")
    data = sales_by_hour(filtered)
    fig = go.Figure(go.Bar(
        x=data["hour"], y=data["orders"],
        marker=dict(
            color=data["orders"],
            colorscale=[[0,"#DBEAFE"],[0.5,"#93C5FD"],[1, BLUE]],
            line_width=0,
        ),
        hovertemplate="<b>%{x}:00</b><br>%{y} orders<extra></extra>",
        text=data["orders"],
        textposition="outside",
    ))
    fig.update_xaxes(title="Hour of day", tickmode="linear", tick0=11, dtick=1)
    fig.update_yaxes(title="Orders")
    show_chart(fig, 280)
    card_end()

    c1, c2 = st.columns(2)
    with c1:
        card_start("Revenue by Day of Week", "Which days generate the most revenue")
        data = sales_by_day(filtered)
        fig = px.bar(data, x="day_of_week", y="revenue",
                     labels={"day_of_week": "", "revenue": "Revenue (£)"},
                     color="revenue",
                     color_continuous_scale=[[0,"#FEF3C7"],[1, ORANGE]])
        fig.update_traces(marker_line_width=0)
        fig.update_layout(coloraxis_showscale=False)
        show_chart(fig, 300)
        card_end()

    with c2:
        card_start("Orders by Day of Week", "Volume of orders per day")
        data = sales_by_day(filtered)
        fig = px.line(data, x="day_of_week", y="orders",
                      labels={"day_of_week": "", "orders": "Orders"},
                      markers=True)
        fig.update_traces(line_color=ORANGE, marker_color=ORANGE,
                          marker_size=9, line_width=3,
                          fill="tozeroy", fillcolor="rgba(245,158,11,0.07)")
        show_chart(fig, 300)
        card_end()

    st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# PAGE: STAFF
# ─────────────────────────────────────────────────────────────────────────────
elif st.session_state.page == "Staff":
    st.markdown('<div class="page-body">', unsafe_allow_html=True)
    st.markdown('<div class="page-title">Staff Performance</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Revenue and order count broken down by server</div>', unsafe_allow_html=True)

    data = server_performance(filtered)

    # KPI row — one card per server
    cols = st.columns(len(data))
    for i, (_, row) in enumerate(data.iterrows()):
        with cols[i]:
            st.markdown(f"""
            <div class="kpi-card" style="text-align:center">
              <div style="font-size:2rem;margin-bottom:8px">👤</div>
              <div class="kpi-label">{row['server']}</div>
              <div class="kpi-value" style="font-size:1.5rem">£{row['revenue']:,.0f}</div>
              <div class="kpi-sub">{int(row['orders'])} orders</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        card_start("Revenue per Server", "Total £ generated by each member of staff")
        fig = px.bar(data, x="server", y="revenue",
                     labels={"server": "", "revenue": "Revenue (£)"},
                     color="server", color_discrete_sequence=PALETTE, text_auto=".0f")
        fig.update_traces(marker_line_width=0, textposition="outside",
                          texttemplate="£%{text}")
        fig.update_layout(showlegend=False, yaxis_range=[0, data["revenue"].max() * 1.15])
        show_chart(fig, 300)
        card_end()

    with c2:
        card_start("Orders per Server", "How many orders each server handled")
        fig = px.bar(data.sort_values("orders", ascending=False),
                     x="server", y="orders",
                     labels={"server": "", "orders": "Orders"},
                     color="server", color_discrete_sequence=PALETTE)
        fig.update_traces(marker_line_width=0)
        fig.update_layout(showlegend=False)
        show_chart(fig, 300)
        card_end()

    # Raw staff table
    st.markdown('<div class="table-card">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title" style="margin-bottom:12px">Full breakdown</div>', unsafe_allow_html=True)
    display = data.copy()
    display["revenue"] = display["revenue"].map("£{:,.2f}".format)
    st.dataframe(display, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
