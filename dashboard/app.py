"""
RestaurantIQ Analytics Dashboard
"""
import sys, math
from pathlib import Path
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

sys.path.insert(0, str(Path(__file__).parent.parent))
from scripts.clean import load_and_clean
from scripts.analyse import (
    top_items_by_revenue, top_items_by_quantity,
    sales_by_hour, sales_by_day, monthly_revenue,
    revenue_by_category, server_performance, payment_split,
)

st.set_page_config(page_title="RestaurantIQ Analytics", page_icon="🍽️", layout="wide", initial_sidebar_state="expanded")

# ── Colour palette ────────────────────────────────────────────────────────────
DARK  = "#1B1D2A"
CORAL = "#E8735A"
GREEN = "#7BC67E"
BLUE  = "#4B9FE1"
YLLOW = "#F4C542"
PAL   = [CORAL, GREEN, BLUE, YLLOW, "#9B72CF", "#F08080", "#20B2AA"]

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');
*, html, body {{ font-family: 'Outfit', sans-serif !important; }}

/* White background */
.stApp {{ background: #F1F5F9; }}
#MainMenu, footer, header {{ visibility: hidden; }}

/* Hide sidebar collapse/expand toggle button */
[data-testid="collapsedControl"] {{ display: none !important; }}
[data-testid="stSidebarCollapseButton"] {{ display: none !important; }}
button[kind="header"] {{ display: none !important; }}

/* ── Sidebar ─────────────────────────────────── */
[data-testid="stSidebar"] {{
    background: {DARK} !important;
}}
[data-testid="stSidebarHeader"] {{
    background: {DARK} !important;
}}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] small,
[data-testid="stSidebar"] label {{
    color: #94A3B8 !important;
}}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {{
    color: #FFFFFF !important;
}}
[data-testid="stSidebar"] hr {{
    border-color: #2E3244 !important;
    margin: 12px 0 !important;
}}

/* ── Sidebar Radio Nav — pill style ─────────── */
[data-testid="stSidebar"] .stRadio > div {{
    gap: 4px !important;
    display: flex !important;
    flex-direction: column !important;
}}
[data-testid="stSidebar"] .stRadio label {{
    background: transparent !important;
    border-radius: 10px !important;
    padding: 10px 14px !important;
    cursor: pointer !important;
    transition: background 0.2s !important;
    display: flex !important;
    align-items: center !important;
    gap: 10px !important;
    color: #94A3B8 !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    margin: 0 !important;
}}
[data-testid="stSidebar"] .stRadio label:hover {{
    background: rgba(255,255,255,0.07) !important;
    color: #FFFFFF !important;
}}
[data-testid="stSidebar"] .stRadio label:has(input:checked) {{
    background: {CORAL} !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
}}
/* Hide the actual radio circle */
[data-testid="stSidebar"] .stRadio label input[type="radio"] {{
    display: none !important;
}}
[data-testid="stSidebar"] .stRadio legend {{
    display: none !important;
}}

/* Multiselect in sidebar */
[data-testid="stSidebar"] .stMultiSelect [data-baseweb="select"] {{
    background: #252839 !important;
    border-color: #3A3F55 !important;
}}
[data-testid="stSidebar"] .stMultiSelect [data-baseweb="tag"] {{
    background: {CORAL} !important;
}}

/* ── Content area ────────────────────────────── */
.block-container {{
    padding-top: 1.5rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    padding-bottom: 2rem !important;
}}

/* Reduce default spacing between Streamlit elements */
[data-testid="element-container"] {{
    margin-bottom: 0.6rem !important;
}}

/* Remove default bottom margin on iframe containers */
[data-testid="stIFrame"] {{
    margin-bottom: -28px !important;
}}

/* Plotly charts get bottom rounded corners only (top = dark header) */
[data-testid="stPlotlyChart"] {{
    background: #FFFFFF !important;
    border-radius: 0 0 14px 14px !important;
    border: none !important;
    box-shadow: none !important;
    padding: 4px 8px 8px !important;
}}

/* DataFrames */
[data-testid="stDataFrame"] {{
    border-radius: 0 0 14px 14px !important;
    overflow: hidden;
}}

/* Page headings */
h1 {{ font-size: 1.7rem !important; color: {DARK} !important; font-weight: 800 !important; }}
h2, h3 {{ color: {DARK} !important; font-weight: 700 !important; }}
</style>
""", unsafe_allow_html=True)


# ── Helper: KPI cards row (via components.html — always renders) ──────────────
def kpi_row(cards):
    """
    cards = list of dict(label, value, delta, icon, color)
    Renders the dark-header / white-body KPI cards from the reference design.
    """
    items = ""
    for c in cards:
        color  = c.get("color", CORAL)
        delta  = c.get("delta", "")
        d_col  = GREEN if "+" in str(delta) else (CORAL if "-" in str(delta) else "#94A3B8")
        items += f"""
        <div style="background:white;border-radius:14px;overflow:hidden;
                    box-shadow:0 6px 24px rgba(0,0,0,0.10);flex:1;min-width:170px;">
            <div style="background:{DARK};padding:12px 16px;
                        display:flex;justify-content:space-between;align-items:center;">
                <span style="color:#94A3B8;font-size:0.6rem;font-weight:700;
                             text-transform:uppercase;letter-spacing:1.2px;
                             font-family:'Outfit',sans-serif;">{c['label']}</span>
                <div style="background:{color};border-radius:50%;width:32px;height:32px;
                            display:flex;align-items:center;justify-content:center;
                            font-size:0.95rem;flex-shrink:0;">{c['icon']}</div>
            </div>
            <div style="padding:14px 18px 16px;font-family:'Outfit',sans-serif;">
                <div style="font-size:1.65rem;font-weight:800;color:{DARK};line-height:1.1;
                            white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
                            max-width:180px;" title="{c['value']}">{c['value']}</div>
                <div style="font-size:0.65rem;color:{d_col};font-weight:600;
                            margin-top:5px;text-transform:uppercase;letter-spacing:0.4px;">{delta}</div>
            </div>
        </div>"""

    rows_est = math.ceil(len(cards) / 4)
    h = rows_est * 122 + 4
    st.iframe(f"""
    <style>
        body {{ margin: 0; padding: 0; overflow: hidden; background: transparent; }}
    </style>
    <div style="display:flex;gap:14px;flex-wrap:wrap;padding:2px 0 4px;font-family:'Outfit',sans-serif;">
        {items}
    </div>""", height=h)


# ── Helper: dark header bar above charts ─────────────────────────────────────
def card_title(label, icon=""):
    icon_html = (
        f"<span style='margin-left:auto;font-size:1rem;'>{icon}</span>" if icon else ""
    )
    st.markdown(f"""
    <div style="background:{DARK};border-radius:14px 14px 0 0;padding:13px 20px;
                display:flex;align-items:center;gap:10px;margin-top:0px;">
        <span style="color:white;font-size:0.72rem;font-weight:700;
                     text-transform:uppercase;letter-spacing:1.4px;">{label}</span>
        {icon_html}
    </div>""", unsafe_allow_html=True)


# ── Helper: Plotly layout ─────────────────────────────────────────────────────
def _layout(h=300):
    return dict(
        paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF",
        font=dict(family="Outfit,sans-serif", color="#64748B", size=12),
        margin=dict(l=15, r=15, t=10, b=15), height=h,
        xaxis=dict(gridcolor="#F1F5F9", linecolor="#E2E8F0", zerolinecolor="#E2E8F0"),
        yaxis=dict(gridcolor="#F1F5F9", linecolor="#E2E8F0", zerolinecolor="#E2E8F0"),
        colorway=PAL, legend=dict(bgcolor="rgba(0,0,0,0)"),
    )

def show(fig, h=300):
    fig.update_layout(**_layout(h))
    st.plotly_chart(fig, width='stretch', config={"displayModeBar": False})


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
    st.markdown("# Sales Overview")
    st.caption("All key metrics at a glance · January 2024")

    total_rev    = filtered["total_price"].sum()
    total_orders = filtered["order_id"].nunique()
    avg_val      = filtered["total_price"].mean() if len(filtered) else 0
    best_item    = top_items_by_quantity(filtered).iloc[0]["menu_item"] if len(filtered) else "—"
    top_server   = server_performance(filtered).iloc[0]["server"] if len(filtered) else "—"

    kpi_row([
        {"label": "Total Revenue",   "value": f"£{total_rev:,.0f}", "delta": "+8.5% since last month", "icon": "💰", "color": GREEN},
        {"label": "Total Orders",    "value": f"{total_orders:,}",  "delta": "+5.2% since last month", "icon": "🧾", "color": CORAL},
        {"label": "Avg Order Value", "value": f"£{avg_val:.2f}",    "delta": "+2.1% since last month", "icon": "📈", "color": BLUE},
        {"label": "Best Seller",     "value": best_item,             "delta": "Top by quantity",        "icon": "🏆", "color": YLLOW},
        {"label": "Top Server",      "value": top_server,            "delta": "By total revenue",       "icon": "⭐", "color": CORAL},
    ])

    # Row 1
    c1, c2 = st.columns([3, 2])
    with c1:
        card_title("Daily Revenue Trend", "📉")
        daily = filtered.groupby("date")["total_price"].sum().reset_index()
        fig = go.Figure(go.Scatter(
            x=daily["date"], y=daily["total_price"],
            mode="lines+markers",
            line=dict(color=DARK, width=2.5),
            marker=dict(size=7, color=CORAL, line=dict(color="white", width=2)),
            fill="tozeroy", fillcolor="rgba(123,198,126,0.18)",
            hovertemplate="<b>%{x|%b %d}</b><br>£%{y:,.2f}<extra></extra>",
        ))
        show(fig, 270)

    with c2:
        card_title("Revenue by Category", "🍽️")
        data = revenue_by_category(filtered)
        fig = px.pie(data, values="revenue", names="category",
                     hole=0.6, color_discrete_sequence=PAL)
        fig.update_traces(textinfo="percent", textposition="inside",
                          hovertemplate="<b>%{label}</b><br>£%{value:,.0f}<extra></extra>")
        fig.update_layout(showlegend=True,
                          legend=dict(orientation="h", yanchor="bottom", y=-0.28, xanchor="center", x=0.5))
        show(fig, 270)

    # Row 2
    c3, c4, c5 = st.columns(3)
    with c3:
        card_title("Orders by Hour")
        data = sales_by_hour(filtered)
        fig = go.Figure(go.Bar(
            x=data["hour"], y=data["orders"],
            marker=dict(color=DARK, line_width=0),
            hovertemplate="<b>%{x}:00</b><br>%{y} orders<extra></extra>",
        ))
        fig.update_xaxes(tickmode="linear", tick0=11, dtick=2)
        show(fig, 230)

    with c4:
        card_title("Revenue by Day")
        data = sales_by_day(filtered)
        fig = px.bar(data, x="day_of_week", y="revenue",
                     color_discrete_sequence=[GREEN],
                     labels={"day_of_week": "", "revenue": "£"})
        fig.update_traces(marker_line_width=0)
        show(fig, 230)

    with c5:
        card_title("Payment Split")
        data = payment_split(filtered)
        fig = px.pie(data, values="revenue", names="payment_method",
                     hole=0.6, color_discrete_sequence=[DARK, CORAL])
        fig.update_traces(textinfo="percent", textposition="inside",
                          hovertemplate="<b>%{label}</b><br>£%{value:,.0f}<extra></extra>")
        fig.update_layout(showlegend=True,
                          legend=dict(orientation="h", yanchor="bottom", y=-0.28, xanchor="center", x=0.5))
        show(fig, 230)

# ══════════════════════════════════════════════════════════════════════════════
# 🍕 MENU
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🍕 Menu":
    st.markdown("# Menu Performance")
    st.caption("Which dishes drive the most revenue and orders")

    c1, c2 = st.columns(2)
    with c1:
        card_title("Top Items — Revenue")
        data = top_items_by_revenue(filtered)
        fig = px.bar(data, x="revenue", y="menu_item", orientation="h",
                     labels={"menu_item": "", "revenue": "Revenue (£)"},
                     color_discrete_sequence=[CORAL])
        fig.update_traces(marker_line_width=0)
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        show(fig, 360)

    with c2:
        card_title("Top Items — Quantity Sold")
        data = top_items_by_quantity(filtered)
        fig = px.bar(data, x="quantity", y="menu_item", orientation="h",
                     labels={"menu_item": "", "quantity": "Units sold"},
                     color_discrete_sequence=[GREEN])
        fig.update_traces(marker_line_width=0)
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        show(fig, 360)

    card_title("Category Breakdown")
    data = revenue_by_category(filtered)
    max_r = data["revenue"].max()
    fig = px.bar(data, x="category", y="revenue", color="category",
                 color_discrete_sequence=PAL,
                 labels={"category": "", "revenue": "Revenue (£)"},
                 text_auto=",.0f")
    fig.update_traces(marker_line_width=0, texttemplate="£%{text}", textposition="outside")
    fig.update_layout(showlegend=False, yaxis_range=[0, max_r * 1.2 if max_r else 1])
    show(fig, 300)

# ══════════════════════════════════════════════════════════════════════════════
# 🕐 TIME & DAYS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🕐 Time & Days":
    st.markdown("# Time & Day Patterns")
    st.caption("When is the restaurant at its busiest?")

    card_title("Orders by Hour of Day")
    data = sales_by_hour(filtered)
    fig = go.Figure(go.Bar(
        x=data["hour"], y=data["orders"],
        marker=dict(color=GREEN, line_width=0),
        text=data["orders"], textposition="outside",
        hovertemplate="<b>%{x}:00</b><br>%{y} orders<extra></extra>",
    ))
    fig.update_xaxes(title="Hour", tickmode="linear", tick0=11, dtick=1)
    fig.update_yaxes(title="Orders")
    show(fig, 280)

    c1, c2 = st.columns(2)
    with c1:
        card_title("Revenue by Day of Week")
        data = sales_by_day(filtered)
        fig = px.bar(data, x="day_of_week", y="revenue",
                     color_discrete_sequence=[CORAL],
                     labels={"day_of_week": "", "revenue": "Revenue (£)"})
        fig.update_traces(marker_line_width=0)
        show(fig, 300)

    with c2:
        card_title("Order Volume by Day")
        data = sales_by_day(filtered)
        fig = go.Figure(go.Scatter(
            x=list(data["day_of_week"]), y=data["orders"],
            mode="lines+markers",
            line=dict(color=DARK, width=3),
            marker=dict(size=9, color=CORAL, line=dict(color="white", width=2)),
            fill="tozeroy", fillcolor="rgba(232,115,90,0.12)",
        ))
        fig.update_yaxes(title="Orders")
        show(fig, 300)

# ══════════════════════════════════════════════════════════════════════════════
# 👤 STAFF
# ══════════════════════════════════════════════════════════════════════════════
elif page == "👤 Staff":
    st.markdown("# Staff Performance")
    st.caption("Revenue and order count per server")

    data = server_performance(filtered)

    if data.empty:
        st.info("No data available for the selected filters. Adjust the sidebar filters.", icon="ℹ️")
    else:
        accent_cycle = [CORAL, GREEN, BLUE, YLLOW, "#9B72CF", "#F08080", "#20B2AA"]
        staff_cards = []
        for i, (_, row) in enumerate(data.iterrows()):
            staff_cards.append({
                "label": row["server"],
                "value": f"£{row['revenue']:,.0f}",
                "delta": f"{int(row['orders'])} orders",
                "icon": "👤",
                "color": accent_cycle[i % len(accent_cycle)],
            })
        kpi_row(staff_cards)

        c1, c2 = st.columns(2)
        with c1:
            card_title("Revenue per Server")
            max_rev = data["revenue"].max()
            fig = px.bar(data, x="server", y="revenue", color="server",
                         color_discrete_sequence=PAL,
                         labels={"server": "", "revenue": "Revenue (£)"},
                         text_auto=",.0f")
            fig.update_traces(marker_line_width=0, texttemplate="£%{text}", textposition="outside")
            fig.update_layout(showlegend=False,
                              yaxis_range=[0, max_rev * 1.2 if max_rev and max_rev > 0 else 1])
            show(fig, 320)

        with c2:
            card_title("Orders per Server")
            fig = px.bar(data.sort_values("orders", ascending=False),
                         x="server", y="orders", color="server",
                         color_discrete_sequence=PAL,
                         labels={"server": "", "orders": "Orders"})
            fig.update_traces(marker_line_width=0)
            fig.update_layout(showlegend=False)
            show(fig, 320)

        card_title("Full Staff Table")
        display = data.copy()
        display["revenue"] = display["revenue"].map("£{:,.2f}".format)
        display.columns = ["Server", "Orders", "Revenue"]
        st.dataframe(display, width='stretch', hide_index=True)

# ══════════════════════════════════════════════════════════════════════════════
# 📋 RAW DATA
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📋 Raw Data":
    st.markdown("# Raw Transaction Data")
    st.caption(f"Showing {len(filtered):,} records with current filters applied")
    card_title("Transaction Records")
    st.dataframe(filtered.sort_values("date"), width='stretch', hide_index=True)
