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
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');
* { font-family: 'Outfit', sans-serif !important; }

/* Hide default Streamlit header */
[data-testid="stHeader"] {
    display: none !important;
}

/* Sidebar Top Header (Inside Sidebar) */
.sidebar-header {
    position: fixed;
    top: 0;
    left: 0;
    width: 336px;
    height: 64px;
    background: #0091EA;
    color: #FFFFFF;
    display: flex;
    align-items: center;
    padding-left: 24px;
    font-size: 1.3rem;
    font-weight: 800;
    letter-spacing: 0.5px;
    z-index: 9999;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

/* Main Top Header (Inside Main Content) */
.main-header {
    position: fixed;
    top: 0;
    right: 0;
    left: 336px;
    height: 64px;
    background: linear-gradient(90deg, #00B0FF 0%, #0091EA 100%);
    color: #FFFFFF;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 32px;
    font-size: 1rem;
    font-weight: 700;
    z-index: 9998;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    transition: left 0.2s ease-in-out;
}
.top-bar-search {
    font-size: 0.85rem;
    letter-spacing: 1px;
    opacity: 0.95;
    font-weight: 700;
    cursor: pointer;
}

/* Handle collapsed sidebar state */
[data-testid="stSidebar"][data-expanded="false"] ~ .main .main-header {
    left: 0 !important;
}

/* Background & Global */
.stApp {
    background: linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 100%);
}
#MainMenu, footer { visibility: hidden; }

/* Custom Container Cards */
.custom-card {
    background: #FFFFFF;
    border-radius: 16px;
    border: 1px solid #E2E8F0;
    padding: 24px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.03), 0 2px 4px -1px rgba(0, 0, 0, 0.02);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    margin-bottom: 20px;
}
.custom-card:hover {
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -4px rgba(0, 0, 0, 0.02);
}

/* Sidebar Styling */
[data-testid="stSidebar"] {
    background-color: #FFFFFF !important;
    border-right: 1px solid #E2E8F0;
    padding-top: 64px !important;
}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2 {
    display: none;
}
[data-testid="stSidebar"] hr {
    margin: 12px 0 !important;
}

/* Navigation List overrides */
[data-testid="stSidebar"] .stRadio label {
    font-size: 0.95rem !important;
    font-weight: 500 !important;
    color: #475569 !important;
    padding: 12px 16px !important;
    border-radius: 8px;
    transition: all 0.2s ease;
    margin: 4px 0 !important;
    display: flex;
    align-items: center;
}
[data-testid="stSidebar"] .stRadio label:hover {
    background: #F1F5F9;
    color: #0F172A !important;
}

/* Hide standard radio dot circles completely */
[data-testid="stSidebar"] [data-baseweb="radio"] input + div {
    display: none !important;
}
[data-testid="stSidebar"] [data-baseweb="radio"] {
    padding: 0 !important;
}

/* Active navigation item styling matching the image */
div[data-baseweb="radio"]:has(input:checked) label {
    color: #0091EA !important;
    font-weight: 700 !important;
    background-color: #E1F5FE !important;
    border-left: 4px solid #0091EA;
    border-radius: 0 8px 8px 0;
    padding-left: 12px !important;
}

/* Adjust main content padding to leave space for top bar */
.main .block-container {
    padding-top: 96px !important;
}

/* KPI Grid */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 16px;
    margin-bottom: 28px;
    width: 100%;
}
@media (max-width: 768px) {
    .kpi-grid {
        grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
        gap: 12px;
    }
    .sidebar-header {
        display: none !important;
    }
    .main-header {
        left: 0 !important;
        padding: 0 16px;
    }
    .main .block-container {
        padding-top: 84px !important;
    }
}
.kpi-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 16px;
    padding: 20px;
    display: flex;
    align-items: center;
    gap: 16px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.03);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.kpi-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 20px -8px rgba(0, 0, 0, 0.08);
    border-color: #0091EA;
}
.kpi-icon {
    font-size: 1.6rem;
    width: 52px;
    height: 52px;
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}
.kpi-info {
    display: flex;
    flex-direction: column;
    overflow: hidden;
}
.kpi-label {
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: #94A3B8 !important;
    margin-bottom: 4px;
}
.kpi-value {
    font-size: 1.45rem !important;
    font-weight: 800 !important;
    color: #0F172A !important;
    line-height: 1.2;
}

/* Charts inside white cards override */
[data-testid="stPlotlyChart"] {
    background: #FFFFFF !important;
    border-radius: 16px !important;
    border: 1px solid #E2E8F0 !important;
    padding: 16px !important;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.03) !important;
    transition: all 0.3s ease;
}
[data-testid="stPlotlyChart"]:hover {
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05) !important;
}

/* Tabs styling */
.stTabs [data-baseweb="tab-list"] {
    background: #E2E8F0;
    border-radius: 12px;
    padding: 4px;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    padding: 10px 24px;
    font-weight: 600;
    font-size: 0.9rem;
    color: #475569;
    background: transparent;
    border: none;
    transition: all 0.2s ease;
}
.stTabs [aria-selected="true"] {
    background: #FFFFFF !important;
    color: #0091EA !important;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

/* Headings */
h1, h2, h3 {
    color: #0F172A !important;
    font-weight: 700 !important;
}
h3 {
    font-size: 1.15rem !important;
    margin-bottom: 8px !important;
}

/* DataFrame */
[data-testid="stDataFrame"] {
    border: 1px solid #E2E8F0;
    border-radius: 12px;
}
</style>

<div class="main-header">
    <span class="top-bar-title">Sales Analytics Dashboard</span>
    <span class="top-bar-search">🔍 SEARCH</span>
</div>
""", unsafe_allow_html=True)

# ── Colours & helpers ─────────────────────────────────────────────────────────
BLUE  = "#0091EA"
CYAN  = "#00B0FF"
INDIGO = "#6366F1"
PAL   = [BLUE, CYAN, INDIGO, "#F59E0B", "#10B981", "#EF4444", "#8B5CF6"]

def _layout(h=300):
    return dict(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Outfit,sans-serif", color="#64748B", size=12),
        margin=dict(l=15, r=15, t=15, b=15), height=h,
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
    st.markdown('<div class="sidebar-header">🍽️ RestaurantIQ</div>', unsafe_allow_html=True)
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

    kpi_html = f"""
    <div class="kpi-grid">
        <div class="kpi-card">
            <div class="kpi-icon" style="background: #ECFDF5; color: #10B981;">💰</div>
            <div class="kpi-info">
                <span class="kpi-label">Revenue</span>
                <span class="kpi-value">£{total_rev:,.0f}</span>
            </div>
        </div>
        <div class="kpi-card">
            <div class="kpi-icon" style="background: #EFF6FF; color: #3B82F6;">🧾</div>
            <div class="kpi-info">
                <span class="kpi-label">Orders</span>
                <span class="kpi-value">{total_orders:,}</span>
            </div>
        </div>
        <div class="kpi-card">
            <div class="kpi-icon" style="background: #FAF5FF; color: #A855F7;">📈</div>
            <div class="kpi-info">
                <span class="kpi-label">Avg Value</span>
                <span class="kpi-value">£{avg_val:.2f}</span>
            </div>
        </div>
        <div class="kpi-card">
            <div class="kpi-icon" style="background: #FFFBEB; color: #F59E0B;">🏆</div>
            <div class="kpi-info">
                <span class="kpi-label">Best Seller</span>
                <span class="kpi-value" style="font-size: 1.1rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="{best_item}">{best_item}</span>
            </div>
        </div>
        <div class="kpi-card">
            <div class="kpi-icon" style="background: #FDF2F8; color: #EC4899;">⭐</div>
            <div class="kpi-info">
                <span class="kpi-label">Top Server</span>
                <span class="kpi-value">{top_server}</span>
            </div>
        </div>
    </div>
    """
    st.markdown(kpi_html, unsafe_allow_html=True)

    # Row 1 — trend + category
    c1, c2 = st.columns([3, 2])

    with c1:
        st.markdown("### Daily Revenue Trend")
        daily = filtered.groupby("date")["total_price"].sum().reset_index()
        fig = go.Figure(go.Scatter(
            x=daily["date"], y=daily["total_price"],
            mode="lines+markers",
            line=dict(color=BLUE, width=3),
            marker=dict(size=8, color=BLUE, line=dict(color="white", width=2)),
            fill="tozeroy", fillcolor="rgba(14,165,233,0.06)",
            hovertemplate="<b>%{x|%b %d}</b><br>£%{y:,.2f}<extra></extra>",
        ))
        show(fig, 280)

    with c2:
        st.markdown("### Revenue by Category")
        data = revenue_by_category(filtered)
        fig = px.pie(data, values="revenue", names="category",
                     hole=0.6, color_discrete_sequence=PAL)
        fig.update_traces(textinfo="percent", textposition="inside",
                          hovertemplate="<b>%{label}</b><br>£%{value:,.0f}<extra></extra>")
        fig.update_layout(showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5))
        show(fig, 280)

    # Row 2 — hours + days + payment
    c3, c4, c5 = st.columns(3)

    with c3:
        st.markdown("### Orders by Hour")
        data = sales_by_hour(filtered)
        fig = go.Figure(go.Bar(
            x=data["hour"], y=data["orders"],
            marker=dict(color=data["orders"],
                        colorscale=[[0,"#E0F2FE"],[1, BLUE]], line_width=0),
            hovertemplate="<b>%{x}:00</b><br>%{y} orders<extra></extra>",
        ))
        fig.update_xaxes(tickmode="linear", tick0=11, dtick=2)
        show(fig, 240)

    with c4:
        st.markdown("### Revenue by Day")
        data = sales_by_day(filtered)
        fig = px.bar(data, x="day_of_week", y="revenue",
                     color="revenue",
                     color_continuous_scale=[[0,"#E0F2FE"],[1,BLUE]],
                     labels={"day_of_week":"","revenue":"£"})
        fig.update_traces(marker_line_width=0)
        fig.update_layout(coloraxis_showscale=False)
        show(fig, 240)

    with c5:
        st.markdown("### Payment Split")
        data = payment_split(filtered)
        fig = px.pie(data, values="revenue", names="payment_method",
                     hole=0.6, color_discrete_sequence=[BLUE, CYAN])
        fig.update_traces(textinfo="percent", textposition="inside",
                          hovertemplate="<b>%{label}</b><br>£%{value:,.0f}<extra></extra>")
        fig.update_layout(showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5))
        show(fig, 240)

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
    # Custom responsive Staff cards
    staff_cards = '<div class="kpi-grid">'
    for _, row in data.iterrows():
        staff_cards += f"""
        <div class="kpi-card">
            <div class="kpi-icon" style="background: #EFF6FF; color: #3B82F6;">👤</div>
            <div class="kpi-info">
                <span class="kpi-label">{row['server']}</span>
                <span class="kpi-value">£{row['revenue']:,.0f}</span>
                <span style="font-size: 0.75rem; color: #64748B; font-weight: 500;">{int(row['orders']):,} orders</span>
            </div>
        </div>
        """
    staff_cards += "</div>"
    st.markdown(staff_cards, unsafe_allow_html=True)

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
