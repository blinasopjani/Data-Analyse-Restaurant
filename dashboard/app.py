import sys
from pathlib import Path
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from clean import load_and_clean
from analyse import (
    top_items_by_revenue, top_items_by_quantity,
    sales_by_hour, sales_by_day, monthly_revenue,
    revenue_by_category, server_performance, payment_split,
)

st.set_page_config(page_title="Restaurant Analytics", page_icon="🍽️", layout="wide")

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

* { font-family: 'Inter', sans-serif !important; box-sizing: border-box; }

.stApp { background: #F0F4F8; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 !important; max-width: 100% !important; }
section[data-testid="stSidebar"] { display: none; }

/* ── TOP HEADER ── */
.top-header {
  background: #fff;
  height: 56px;
  display: flex;
  align-items: center;
  padding: 0 28px;
  border-bottom: 1px solid #E8EEF4;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
  position: sticky; top: 0; z-index: 100;
}
.logo { font-size: 1rem; font-weight: 800; color: #0EA5E9; letter-spacing: -0.3px; }
.logo span { color: #1E293B; font-weight: 400; }
.header-search {
  margin-left: auto;
  display: flex; align-items: center; gap: 6px;
  color: #94A3B8; font-size: 0.82rem; font-weight: 500;
  cursor: pointer;
}
.header-search:hover { color: #0EA5E9; }

/* ── LAYOUT WRAPPER ── */
.layout { display: flex; min-height: calc(100vh - 56px); }

/* ── LEFT NAV ── */
.left-nav {
  width: 200px;
  min-width: 200px;
  background: #fff;
  border-right: 1px solid #E8EEF4;
  padding: 24px 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.nav-section {
  padding: 16px 20px 6px;
  font-size: 0.68rem;
  font-weight: 700;
  color: #94A3B8;
  letter-spacing: 1.2px;
  text-transform: uppercase;
}
.nav-item {
  display: flex; align-items: center; gap: 10px;
  padding: 9px 20px;
  font-size: 0.855rem;
  font-weight: 500;
  color: #64748B;
  cursor: pointer;
  border-left: 3px solid transparent;
  transition: all .15s;
  text-decoration: none;
}
.nav-item:hover { background: #F0F9FF; color: #0EA5E9; }
.nav-item.active {
  background: #F0F9FF;
  color: #0EA5E9;
  border-left-color: #0EA5E9;
  font-weight: 600;
}
.nav-icon { font-size: 1rem; width: 20px; text-align: center; }

/* ── MAIN CONTENT ── */
.main-content { flex: 1; padding: 28px 28px 40px; overflow-x: hidden; }

/* ── PAGE TITLE ── */
.page-title {
  font-size: 1.25rem; font-weight: 700; color: #1E293B; margin-bottom: 4px;
}
.page-sub { font-size: 0.82rem; color: #94A3B8; margin-bottom: 24px; }

/* ── METRIC CARDS ── */
.metric-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 20px; }
.metric-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px 22px 14px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
  border: 1px solid #E8EEF4;
  position: relative; overflow: hidden;
}
.metric-card.accent {
  background: linear-gradient(135deg, #0EA5E9 0%, #06B6D4 100%);
  border: none;
}
.metric-label {
  font-size: 0.72rem; font-weight: 600; color: #94A3B8;
  text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 6px;
}
.metric-card.accent .metric-label { color: rgba(255,255,255,0.75); }
.metric-value {
  font-size: 1.75rem; font-weight: 800; color: #1E293B; line-height: 1;
}
.metric-card.accent .metric-value { color: #fff; font-size: 2.2rem; }
.metric-sub { font-size: 0.75rem; color: #94A3B8; margin-top: 6px; }
.metric-card.accent .metric-sub { color: rgba(255,255,255,0.7); }

/* ── CHART CARDS ── */
.card {
  background: #fff;
  border-radius: 12px;
  padding: 20px 22px 10px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
  border: 1px solid #E8EEF4;
  margin-bottom: 16px;
}
.card-title {
  font-size: 0.82rem; font-weight: 600; color: #94A3B8;
  text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 2px;
}
.card-value {
  font-size: 1.5rem; font-weight: 800; color: #0EA5E9;
}
.card-heading { font-size: 0.92rem; font-weight: 700; color: #1E293B; margin-bottom: 14px; }

/* ── PROGRESS BARS ── */
.prog-row { margin-bottom: 14px; }
.prog-label { display: flex; justify-content: space-between; margin-bottom: 5px; }
.prog-name { font-size: 0.8rem; font-weight: 500; color: #475569; }
.prog-val { font-size: 0.8rem; font-weight: 700; color: #0EA5E9; }
.prog-track { background: #E8EEF4; border-radius: 99px; height: 7px; }
.prog-fill { height: 7px; border-radius: 99px; background: linear-gradient(90deg,#0EA5E9,#06B6D4); }

/* ── TWO-COL STAT ── */
.stat-pair { display: flex; gap: 12px; margin-top: 4px; }
.stat-box { flex: 1; }
.stat-num { font-size: 1.6rem; font-weight: 800; color: #fff; }
.stat-lbl { font-size: 0.7rem; color: rgba(255,255,255,0.7); margin-top: 2px; }

/* Plotly container padding fix */
.js-plotly-plot { margin: 0 !important; }
</style>
""", unsafe_allow_html=True)

# ── Data ──────────────────────────────────────────────────────────────────────
df = load_and_clean()

# ── Nav state ─────────────────────────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

PAGES = {
    "Dashboard": "🏠",
    "Menu":      "🍕",
    "Time":      "🕐",
    "Staff":     "👤",
    "Raw Data":  "📋",
}

# ── Shared filters (stored in state) ─────────────────────────────────────────
if "days" not in st.session_state:
    st.session_state.days = list(df["day_of_week"].cat.categories)
if "cats" not in st.session_state:
    st.session_state.cats = sorted(df["category"].unique())

filtered = df[df["day_of_week"].isin(st.session_state.days) & df["category"].isin(st.session_state.cats)]

# ── Plotly helper ─────────────────────────────────────────────────────────────
BLUE  = "#0EA5E9"
CYAN  = "#06B6D4"
NAVY  = "#1E293B"
PAL   = [BLUE, CYAN, "#6366F1", "#F59E0B", "#10B981", "#EF4444", "#8B5CF6"]

def _base(height=260):
    return dict(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter,sans-serif", color="#64748B", size=11),
        margin=dict(l=8, r=8, t=8, b=8), height=height,
        xaxis=dict(gridcolor="#F1F5F9", linecolor="#E8EEF4", zerolinecolor="#E8EEF4"),
        yaxis=dict(gridcolor="#F1F5F9", linecolor="#E8EEF4", zerolinecolor="#E8EEF4"),
        colorway=PAL, legend=dict(bgcolor="rgba(0,0,0,0)"),
    )

def show(fig, height=260):
    fig.update_layout(**_base(height))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

def sparkline(values, color=BLUE):
    fig = go.Figure(go.Scatter(
        y=values, mode="lines",
        line=dict(color=color, width=2),
        fill="tozeroy", fillcolor=f"rgba(14,165,233,0.08)",
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0,r=0,t=0,b=0), height=44,
        xaxis=dict(visible=False), yaxis=dict(visible=False),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# ══════════════════════════════════════════════════════════════════════════════
# RENDER
# ══════════════════════════════════════════════════════════════════════════════

# ── Top header ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="top-header">
  <div class="logo">RESTAURANT<span>IQ</span></div>
  <div class="header-search">🔍 &nbsp;Search</div>
</div>
""", unsafe_allow_html=True)

# ── Layout: nav + content ─────────────────────────────────────────────────────
nav_col, main_col = st.columns([1, 5])

# ── Left nav ──────────────────────────────────────────────────────────────────
with nav_col:
    st.markdown('<div class="left-nav">', unsafe_allow_html=True)
    st.markdown('<div class="nav-section">MAIN</div>', unsafe_allow_html=True)

    for label, icon in PAGES.items():
        active_class = "active" if st.session_state.page == label else ""
        st.markdown(f'<div class="nav-item {active_class}">{icon}&nbsp;&nbsp;{label}</div>', unsafe_allow_html=True)
        if st.button(label, key=f"nav_{label}", use_container_width=True):
            st.session_state.page = label
            st.rerun()

    st.markdown('<div class="nav-section">FILTERS</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    with st.expander("Days"):
        days_sel = st.multiselect("", ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],
                                  default=st.session_state.days, label_visibility="collapsed", key="days_filter")
        st.session_state.days = days_sel

    with st.expander("Category"):
        cats_sel = st.multiselect("", sorted(df["category"].unique()),
                                  default=st.session_state.cats, label_visibility="collapsed", key="cats_filter")
        st.session_state.cats = cats_sel

# ── Main content ──────────────────────────────────────────────────────────────
with main_col:

    # ── DASHBOARD ──────────────────────────────────────────────────────────
    if st.session_state.page == "Dashboard":
        st.markdown('<div class="page-title">Dashboard</div>', unsafe_allow_html=True)
        st.markdown('<div class="page-sub">Restaurant sales overview · January 2024</div>', unsafe_allow_html=True)

        total_rev    = filtered["total_price"].sum()
        total_orders = filtered["order_id"].nunique()
        avg_val      = filtered["total_price"].mean() if len(filtered) else 0
        top_cat      = revenue_by_category(filtered).iloc[0]["category"] if len(filtered) else "—"
        daily_rev    = filtered.groupby("date")["total_price"].sum().values

        # KPI row
        m1, m2, m3, m4 = st.columns([1,1,1,1])

        with m1:
            st.markdown(f"""
            <div class="metric-card">
              <div class="metric-label">Total Revenue</div>
              <div class="metric-value">£{total_rev:,.0f}</div>
              <div class="metric-sub">January 2024</div>
            </div>""", unsafe_allow_html=True)
            sparkline(daily_rev)

        with m2:
            st.markdown(f"""
            <div class="metric-card">
              <div class="metric-label">Total Orders</div>
              <div class="metric-value">{total_orders:,}</div>
              <div class="metric-sub">Unique transactions</div>
            </div>""", unsafe_allow_html=True)
            sparkline(daily_rev, CYAN)

        with m3:
            st.markdown(f"""
            <div class="metric-card">
              <div class="metric-label">Avg Order Value</div>
              <div class="metric-value">£{avg_val:.2f}</div>
              <div class="metric-sub">Per transaction</div>
            </div>""", unsafe_allow_html=True)
            sparkline(daily_rev, "#6366F1")

        with m4:
            top_item = top_items_by_quantity(filtered).iloc[0] if len(filtered) else None
            qty  = int(top_item["quantity"]) if top_item is not None else 0
            orders_cnt = total_orders
            st.markdown(f"""
            <div class="metric-card accent">
              <div class="metric-label">Best Seller</div>
              <div class="stat-pair">
                <div class="stat-box">
                  <div class="stat-num">{qty}</div>
                  <div class="stat-lbl">units sold</div>
                </div>
                <div class="stat-box">
                  <div class="stat-num">{orders_cnt}</div>
                  <div class="stat-lbl">orders</div>
                </div>
              </div>
              <div class="metric-sub" style="margin-top:8px">{top_item['menu_item'] if top_item is not None else '—'}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

        # Row 2: donut + line chart + stats
        r1, r2, r3 = st.columns([1, 2.2, 1.1])

        with r1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title">Category Split</div>', unsafe_allow_html=True)
            data = revenue_by_category(filtered)
            pct  = round(data.iloc[0]["revenue"] / data["revenue"].sum() * 100) if len(data) else 0
            st.markdown(f'<div class="card-value">{pct}%</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="font-size:0.75rem;color:#94A3B8;margin-bottom:10px">{data.iloc[0]["category"] if len(data) else ""}</div>', unsafe_allow_html=True)
            fig = px.pie(data, values="revenue", names="category", hole=0.62,
                         color_discrete_sequence=PAL)
            fig.update_traces(textinfo="none",
                              hovertemplate="<b>%{label}</b><br>£%{value:,.0f}<extra></extra>")
            fig.update_layout(**_base(160), showlegend=False,
                              margin=dict(l=0,r=0,t=0,b=0))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

            st.markdown('<div class="card-title" style="margin-top:16px">Payment</div>', unsafe_allow_html=True)
            pay = payment_split(filtered)
            pay_pct = round(pay.iloc[0]["revenue"] / pay["revenue"].sum() * 100) if len(pay) else 0
            st.markdown(f'<div class="card-value">{pay_pct}%</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="font-size:0.75rem;color:#94A3B8;margin-bottom:10px">{pay.iloc[0]["payment_method"] if len(pay) else ""}</div>', unsafe_allow_html=True)
            fig2 = px.pie(pay, values="revenue", names="payment_method", hole=0.62,
                          color_discrete_sequence=[BLUE, CYAN])
            fig2.update_traces(textinfo="none")
            fig2.update_layout(**_base(140), showlegend=False,
                               margin=dict(l=0,r=0,t=0,b=0))
            st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
            st.markdown('</div>', unsafe_allow_html=True)

        with r2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-heading">Daily Revenue Trend</div>', unsafe_allow_html=True)
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
            show(fig, 220)

            st.markdown('<div class="card-heading" style="margin-top:16px">Orders by Hour</div>', unsafe_allow_html=True)
            data = sales_by_hour(filtered)
            fig = go.Figure(go.Bar(
                x=data["hour"], y=data["orders"],
                marker=dict(
                    color=data["orders"],
                    colorscale=[[0,"#DBEAFE"],[1, BLUE]],
                    line_width=0,
                ),
                hovertemplate="<b>%{x}:00</b><br>%{y} orders<extra></extra>",
            ))
            fig.update_xaxes(title="Hour", tickmode="linear", tick0=11, dtick=1)
            show(fig, 180)
            st.markdown('</div>', unsafe_allow_html=True)

        with r3:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-heading">Top Items</div>', unsafe_allow_html=True)
            items = top_items_by_revenue(filtered).head(5)
            max_rev = items["revenue"].max()
            for _, row in items.iterrows():
                pct = int(row["revenue"] / max_rev * 100)
                st.markdown(f"""
                <div class="prog-row">
                  <div class="prog-label">
                    <span class="prog-name">{row['menu_item']}</span>
                    <span class="prog-val">£{row['revenue']:,.0f}</span>
                  </div>
                  <div class="prog-track"><div class="prog-fill" style="width:{pct}%"></div></div>
                </div>""", unsafe_allow_html=True)

            st.markdown('<div class="card-heading" style="margin-top:20px">Revenue by Day</div>', unsafe_allow_html=True)
            data = sales_by_day(filtered)
            fig = px.bar(data, x="day_of_week", y="revenue",
                         labels={"day_of_week":"","revenue":"£"},
                         color="revenue",
                         color_continuous_scale=[[0,"#DBEAFE"],[1, BLUE]])
            fig.update_traces(marker_line_width=0)
            fig.update_layout(coloraxis_showscale=False)
            show(fig, 200)
            st.markdown('</div>', unsafe_allow_html=True)

    # ── MENU ───────────────────────────────────────────────────────────────
    elif st.session_state.page == "Menu":
        st.markdown('<div class="page-title">Menu Performance</div>', unsafe_allow_html=True)
        st.markdown('<div class="page-sub">Which dishes drive revenue and orders</div>', unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="card"><div class="card-heading">Top Items by Revenue</div>', unsafe_allow_html=True)
            data = top_items_by_revenue(filtered)
            fig = px.bar(data, x="revenue", y="menu_item", orientation="h",
                         labels={"menu_item":"","revenue":"Revenue (£)"},
                         color="revenue", color_continuous_scale=[[0,"#DBEAFE"],[1,BLUE]])
            fig.update_traces(marker_line_width=0)
            fig.update_layout(coloraxis_showscale=False, yaxis={"categoryorder":"total ascending"})
            show(fig, 340)
            st.markdown('</div>', unsafe_allow_html=True)

        with c2:
            st.markdown('<div class="card"><div class="card-heading">Top Items by Quantity</div>', unsafe_allow_html=True)
            data = top_items_by_quantity(filtered)
            fig = px.bar(data, x="quantity", y="menu_item", orientation="h",
                         labels={"menu_item":"","quantity":"Units sold"},
                         color="quantity", color_continuous_scale=[[0,"#CFFAFE"],[1,CYAN]])
            fig.update_traces(marker_line_width=0)
            fig.update_layout(coloraxis_showscale=False, yaxis={"categoryorder":"total ascending"})
            show(fig, 340)
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="card"><div class="card-heading">Category Revenue</div>', unsafe_allow_html=True)
        data = revenue_by_category(filtered)
        fig = px.bar(data, x="category", y="revenue", color="category",
                     color_discrete_sequence=PAL, labels={"category":"","revenue":"Revenue (£)"},
                     text_auto=",.0f")
        fig.update_traces(marker_line_width=0, texttemplate="£%{text}", textposition="outside")
        fig.update_layout(showlegend=False, yaxis_range=[0, data["revenue"].max()*1.2])
        show(fig, 280)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── TIME ────────────────────────────────────────────────────────────────
    elif st.session_state.page == "Time":
        st.markdown('<div class="page-title">Time & Day Patterns</div>', unsafe_allow_html=True)
        st.markdown('<div class="page-sub">When is the restaurant at its busiest?</div>', unsafe_allow_html=True)

        st.markdown('<div class="card"><div class="card-heading">Orders by Hour of Day</div>', unsafe_allow_html=True)
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
        show(fig, 260)
        st.markdown('</div>', unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="card"><div class="card-heading">Revenue by Day</div>', unsafe_allow_html=True)
            data = sales_by_day(filtered)
            fig = px.bar(data, x="day_of_week", y="revenue",
                         color="revenue", color_continuous_scale=[[0,"#DBEAFE"],[1,BLUE]],
                         labels={"day_of_week":"","revenue":"Revenue (£)"})
            fig.update_traces(marker_line_width=0)
            fig.update_layout(coloraxis_showscale=False)
            show(fig, 280)
            st.markdown('</div>', unsafe_allow_html=True)

        with c2:
            st.markdown('<div class="card"><div class="card-heading">Orders by Day</div>', unsafe_allow_html=True)
            data = sales_by_day(filtered)
            fig = go.Figure(go.Scatter(
                x=list(data["day_of_week"]), y=data["orders"],
                mode="lines+markers",
                line=dict(color=CYAN, width=3),
                marker=dict(size=9, color=CYAN, line=dict(color="white",width=2)),
                fill="tozeroy", fillcolor="rgba(6,182,212,0.08)",
            ))
            show(fig, 280)
            st.markdown('</div>', unsafe_allow_html=True)

    # ── STAFF ───────────────────────────────────────────────────────────────
    elif st.session_state.page == "Staff":
        st.markdown('<div class="page-title">Staff Performance</div>', unsafe_allow_html=True)
        st.markdown('<div class="page-sub">Revenue and orders per server</div>', unsafe_allow_html=True)

        data = server_performance(filtered)
        cols = st.columns(len(data))
        for col, (_, row) in zip(cols, data.iterrows()):
            col.markdown(f"""
            <div class="metric-card" style="text-align:center">
              <div style="font-size:1.8rem;margin-bottom:8px">👤</div>
              <div class="metric-label">{row['server']}</div>
              <div class="metric-value" style="font-size:1.4rem">£{row['revenue']:,.0f}</div>
              <div class="metric-sub">{int(row['orders'])} orders</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)

        with c1:
            st.markdown('<div class="card"><div class="card-heading">Revenue per Server</div>', unsafe_allow_html=True)
            fig = px.bar(data, x="server", y="revenue", color="server",
                         color_discrete_sequence=PAL,
                         labels={"server":"","revenue":"Revenue (£)"}, text_auto=",.0f")
            fig.update_traces(marker_line_width=0, texttemplate="£%{text}", textposition="outside")
            fig.update_layout(showlegend=False, yaxis_range=[0, data["revenue"].max()*1.18])
            show(fig, 300)
            st.markdown('</div>', unsafe_allow_html=True)

        with c2:
            st.markdown('<div class="card"><div class="card-heading">Top Items Progress</div>', unsafe_allow_html=True)
            items = top_items_by_revenue(filtered).head(6)
            max_r = items["revenue"].max()
            for _, row in items.iterrows():
                pct = int(row["revenue"] / max_r * 100)
                st.markdown(f"""
                <div class="prog-row">
                  <div class="prog-label">
                    <span class="prog-name">{row['menu_item']}</span>
                    <span class="prog-val">£{row['revenue']:,.0f}</span>
                  </div>
                  <div class="prog-track"><div class="prog-fill" style="width:{pct}%"></div></div>
                </div>""", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # ── RAW DATA ────────────────────────────────────────────────────────────
    elif st.session_state.page == "Raw Data":
        st.markdown('<div class="page-title">Raw Data</div>', unsafe_allow_html=True)
        st.markdown('<div class="page-sub">Full transaction table with filters applied</div>', unsafe_allow_html=True)
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.dataframe(filtered.sort_values("date"), use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)
