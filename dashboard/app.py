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

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Restaurant Analytics",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Theme colours ─────────────────────────────────────────────────────────────
PRIMARY   = "#FF6B35"
SECONDARY = "#2C3E50"
BG_CARD   = "#1E1E2E"
BG_PAGE   = "#13131F"
TEXT      = "#E0E0E0"
MUTED     = "#8B8FA8"
GREEN     = "#2ECC71"
PALETTE   = [PRIMARY, "#F7C59F", "#EFEFD0", "#004E89", "#1A936F", "#C84B31", "#88D498"]

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
  /* ── Page background ── */
  .stApp {{ background-color: {BG_PAGE}; }}

  /* ── Sidebar ── */
  [data-testid="stSidebar"] {{
    background-color: {BG_CARD};
    border-right: 1px solid #2A2A3E;
  }}
  [data-testid="stSidebar"] * {{ color: {TEXT} !important; }}

  /* ── Hide default header ── */
  header[data-testid="stHeader"] {{ background: transparent; }}

  /* ── KPI cards ── */
  .kpi-card {{
    background: {BG_CARD};
    border: 1px solid #2A2A3E;
    border-radius: 16px;
    padding: 24px 28px;
    text-align: center;
    box-shadow: 0 4px 24px rgba(0,0,0,0.3);
    transition: transform .2s;
  }}
  .kpi-card:hover {{ transform: translateY(-3px); }}
  .kpi-label {{
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: {MUTED};
    margin-bottom: 8px;
  }}
  .kpi-value {{
    font-size: 2.1rem;
    font-weight: 800;
    color: {TEXT};
    line-height: 1;
  }}
  .kpi-accent {{ color: {PRIMARY}; }}

  /* ── Section headers ── */
  .section-title {{
    font-size: 1rem;
    font-weight: 700;
    letter-spacing: 0.5px;
    color: {TEXT};
    margin-bottom: 4px;
  }}
  .section-sub {{
    font-size: 0.78rem;
    color: {MUTED};
    margin-bottom: 16px;
  }}

  /* ── Chart wrapper ── */
  .chart-card {{
    background: {BG_CARD};
    border: 1px solid #2A2A3E;
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0 4px 24px rgba(0,0,0,0.2);
  }}

  /* ── Divider ── */
  hr {{ border-color: #2A2A3E !important; }}

  /* ── Plotly chart bg ── */
  .js-plotly-plot .plotly .bg {{ fill: transparent !important; }}

  /* ── Dataframe ── */
  [data-testid="stDataFrame"] {{ border-radius: 12px; overflow: hidden; }}

  /* ── Scrollbar ── */
  ::-webkit-scrollbar {{ width: 6px; }}
  ::-webkit-scrollbar-track {{ background: {BG_PAGE}; }}
  ::-webkit-scrollbar-thumb {{ background: #2A2A3E; border-radius: 3px; }}
</style>
""", unsafe_allow_html=True)

# ── Plotly base layout ────────────────────────────────────────────────────────
CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color=TEXT, size=12),
    margin=dict(l=10, r=10, t=10, b=10),
    xaxis=dict(gridcolor="#2A2A3E", linecolor="#2A2A3E", zerolinecolor="#2A2A3E"),
    yaxis=dict(gridcolor="#2A2A3E", linecolor="#2A2A3E", zerolinecolor="#2A2A3E"),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="#2A2A3E"),
    colorway=PALETTE,
)


def chart(fig, height=340):
    fig.update_layout(**CHART_LAYOUT, height=height)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# ── Data ──────────────────────────────────────────────────────────────────────
df = load_and_clean()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"<div style='font-size:1.5rem;font-weight:800;color:{PRIMARY};margin-bottom:4px'>🍽️ RestaurantIQ</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:0.75rem;color:{MUTED};margin-bottom:24px'>Sales Analytics Dashboard</div>", unsafe_allow_html=True)
    st.markdown("---")

    st.markdown(f"<div style='font-size:0.78rem;font-weight:700;letter-spacing:1px;color:{MUTED};margin-bottom:8px'>FILTERS</div>", unsafe_allow_html=True)

    days = st.multiselect(
        "Days of week",
        options=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
        default=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
    )
    categories = st.multiselect(
        "Categories",
        options=sorted(df["category"].unique()),
        default=sorted(df["category"].unique()),
    )
    servers = st.multiselect(
        "Servers",
        options=sorted(df["server"].unique()),
        default=sorted(df["server"].unique()),
    )

    st.markdown("---")
    st.markdown(f"<div style='font-size:0.72rem;color:{MUTED}'>Dataset: {len(df):,} rows · Jan 2024</div>", unsafe_allow_html=True)

filtered = df[
    df["day_of_week"].isin(days) &
    df["category"].isin(categories) &
    df["server"].isin(servers)
]

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style='margin-bottom:8px'>
  <span style='font-size:1.9rem;font-weight:800;color:{TEXT}'>Sales Overview</span>
  <span style='font-size:0.85rem;color:{MUTED};margin-left:12px'>January 2024</span>
</div>
""", unsafe_allow_html=True)

# ── KPI row ───────────────────────────────────────────────────────────────────
total_rev   = filtered["total_price"].sum()
total_orders = filtered["order_id"].nunique()
avg_order   = filtered["total_price"].mean()
best_item   = top_items_by_quantity(filtered).iloc[0]["menu_item"] if len(filtered) else "—"
top_server  = server_performance(filtered).iloc[0]["server"] if len(filtered) else "—"

k1, k2, k3, k4, k5 = st.columns(5)

for col, label, value in [
    (k1, "Total Revenue",    f"£{total_rev:,.0f}"),
    (k2, "Total Orders",     f"{total_orders:,}"),
    (k3, "Avg Order Value",  f"£{avg_order:.2f}"),
    (k4, "Best Seller",      best_item),
    (k5, "Top Server",       top_server),
]:
    col.markdown(f"""
    <div class="kpi-card">
      <div class="kpi-label">{label}</div>
      <div class="kpi-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='margin:24px 0 8px'></div>", unsafe_allow_html=True)

# ── Row 1: Top items + Category donut ────────────────────────────────────────
c1, c2 = st.columns([3, 2])

with c1:
    st.markdown(f"<div class='section-title'>Top Items by Revenue</div><div class='section-sub'>Ranked by total £ generated</div>", unsafe_allow_html=True)
    data = top_items_by_revenue(filtered)
    fig = px.bar(
        data, x="revenue", y="menu_item", orientation="h",
        labels={"menu_item": "", "revenue": "Revenue (£)"},
        color="revenue", color_continuous_scale=[[0, "#2C3E50"], [1, PRIMARY]],
    )
    fig.update_traces(marker_line_width=0)
    fig.update_layout(coloraxis_showscale=False, yaxis={"categoryorder": "total ascending"})
    chart(fig)

with c2:
    st.markdown(f"<div class='section-title'>Revenue by Category</div><div class='section-sub'>Share of total sales</div>", unsafe_allow_html=True)
    data = revenue_by_category(filtered)
    fig = px.pie(data, values="revenue", names="category", hole=0.55, color_discrete_sequence=PALETTE)
    fig.update_traces(textposition="outside", textinfo="label+percent", hovertemplate="<b>%{label}</b><br>£%{value:,.2f}<extra></extra>")
    fig.update_layout(showlegend=False)
    chart(fig)

# ── Row 2: Hourly + Day of week ───────────────────────────────────────────────
c3, c4 = st.columns(2)

with c3:
    st.markdown(f"<div class='section-title'>Busiest Hours</div><div class='section-sub'>Order volume by hour of day</div>", unsafe_allow_html=True)
    data = sales_by_hour(filtered)
    fig = go.Figure(go.Bar(
        x=data["hour"], y=data["orders"],
        marker=dict(
            color=data["orders"],
            colorscale=[[0, "#2C3E50"], [1, PRIMARY]],
            line_width=0,
        ),
        hovertemplate="<b>%{x}:00</b><br>%{y} orders<extra></extra>",
    ))
    fig.update_xaxes(tickmode="linear", tick0=10, dtick=1, title="Hour")
    fig.update_yaxes(title="Orders")
    chart(fig)

with c4:
    st.markdown(f"<div class='section-title'>Revenue by Day</div><div class='section-sub'>Which days bring in the most</div>", unsafe_allow_html=True)
    data = sales_by_day(filtered)
    fig = px.bar(
        data, x="day_of_week", y="revenue",
        labels={"day_of_week": "", "revenue": "Revenue (£)"},
        color="revenue", color_continuous_scale=[[0, "#2C3E50"], [1, "#1A936F"]],
    )
    fig.update_traces(marker_line_width=0)
    fig.update_layout(coloraxis_showscale=False)
    chart(fig)

# ── Row 3: Monthly trend + Server perf ───────────────────────────────────────
c5, c6 = st.columns([3, 2])

with c5:
    st.markdown(f"<div class='section-title'>Monthly Revenue Trend</div><div class='section-sub'>Revenue over time</div>", unsafe_allow_html=True)
    data = monthly_revenue(filtered)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data["month"], y=data["revenue"],
        mode="lines+markers",
        line=dict(color=PRIMARY, width=3),
        marker=dict(size=8, color=PRIMARY, line=dict(color=BG_CARD, width=2)),
        fill="tozeroy",
        fillcolor="rgba(255,107,53,0.08)",
        hovertemplate="<b>%{x}</b><br>£%{y:,.2f}<extra></extra>",
    ))
    fig.update_yaxes(title="Revenue (£)")
    chart(fig, height=300)

with c6:
    st.markdown(f"<div class='section-title'>Server Performance</div><div class='section-sub'>Revenue generated per server</div>", unsafe_allow_html=True)
    data = server_performance(filtered)
    fig = px.bar(
        data, x="server", y="revenue",
        labels={"server": "", "revenue": "Revenue (£)"},
        color="revenue", color_continuous_scale=[[0, "#2C3E50"], [1, "#004E89"]],
    )
    fig.update_traces(marker_line_width=0)
    fig.update_layout(coloraxis_showscale=False)
    chart(fig, height=300)

# ── Row 4: Payment split + Top items by qty ───────────────────────────────────
c7, c8 = st.columns(2)

with c7:
    st.markdown(f"<div class='section-title'>Payment Method Split</div><div class='section-sub'>Card vs cash breakdown</div>", unsafe_allow_html=True)
    data = payment_split(filtered)
    fig = px.pie(data, values="revenue", names="payment_method", hole=0.55,
                 color_discrete_sequence=[PRIMARY, "#004E89"])
    fig.update_traces(textposition="outside", textinfo="label+percent",
                      hovertemplate="<b>%{label}</b><br>£%{value:,.2f}<extra></extra>")
    fig.update_layout(showlegend=False)
    chart(fig, height=280)

with c8:
    st.markdown(f"<div class='section-title'>Top Items by Quantity</div><div class='section-sub'>Most ordered items</div>", unsafe_allow_html=True)
    data = top_items_by_quantity(filtered)
    fig = px.bar(
        data, x="quantity", y="menu_item", orientation="h",
        labels={"menu_item": "", "quantity": "Units sold"},
        color="quantity", color_continuous_scale=[[0, "#2C3E50"], [1, "#1A936F"]],
    )
    fig.update_traces(marker_line_width=0)
    fig.update_layout(coloraxis_showscale=False, yaxis={"categoryorder": "total ascending"})
    chart(fig, height=280)

# ── Raw data expander ─────────────────────────────────────────────────────────
st.markdown("<div style='margin-top:16px'></div>", unsafe_allow_html=True)
with st.expander("Raw data table"):
    st.dataframe(
        filtered.sort_values("date"),
        use_container_width=True,
        hide_index=True,
    )
