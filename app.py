import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ── Page Config (MUST be first) ───────────────────────────────────────────────
st.set_page_config(page_title="VIX Fear Index Dashboard", layout="wide", page_icon="📈")

# ── Google Font + CSS ─────────────────────────────────────────────────────────
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=EB+Garamond:wght@400;600;700&display=swap" rel="stylesheet">
<style>
    html, body, [class*="css"], .stMarkdown, p, div, span, label {
        font-family: 'EB Garamond', Georgia, serif !important;
    }
    .main-title { font-size: 2.3rem; font-weight: 700; margin-bottom: 0.2rem; }
    .sub-title   { color: #888; font-size: 0.95rem; margin-bottom: 1.2rem; }
    .chart-title { font-size: 1.15rem; font-weight: 600; margin: 1.6rem 0 0.2rem; color: #e0e0e0; }
    .chart-desc  { font-size: 0.85rem; color: #777; margin-bottom: 0.4rem; }
    .metric-box  {
        background: #13131f; border: 1px solid #2a2a3d;
        border-radius: 10px; padding: 1rem 1.2rem; text-align: center;
    }
    .metric-lbl  { font-size: 0.75rem; color: #777; text-transform: uppercase; letter-spacing: 0.08em; }
    .metric-val  { font-size: 2rem; font-weight: 700; margin-top: 4px; }
    hr.divider   { border: none; border-top: 1px solid #2a2a3d; margin: 1.2rem 0; }
    /* Hide sidebar collapse arrow button */
    button[kind="headerNoPadding"], [data-testid="collapsedControl"] { display: none !important; }
    section[data-testid="stSidebarCollapsedControl"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

# ── Load & Prepare Data ───────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("vix-daily-cleaned.csv")
    df["DATE"]   = pd.to_datetime(df["DATE"])
    df["MA_30"]  = df["CLOSE"].rolling(30).mean()
    df["MA_252"] = df["CLOSE"].rolling(252).mean()
    df["Year"]   = df["DATE"].dt.year
    df["Month"]  = df["DATE"].dt.month
    df["Zone"]   = pd.cut(
        df["CLOSE"],
        bins=[0, 15, 25, 35, 9999],
        labels=["Low (<15)", "Normal (15-25)", "High (25-35)", "Extreme (>35)"]
    )
    return df

df = load_data()

ZONE_COLORS = {
    "Low (<15)":     "#2ecc71",
    "Normal (15-25)":"#3498db",
    "High (25-35)":  "#e67e22",
    "Extreme (>35)": "#e74c3c"
}

CRISES = [
    ("1997-10-27", "Asian Crisis '97",  0.88),
    ("2001-09-11", "9/11 Attack",       0.78),
    ("2008-10-24", "2008 Crash",        0.95),
    ("2010-05-06", "Flash Crash '10",   0.68),
    ("2020-03-16", "COVID-19 Peak",     0.95),
    ("2022-03-07", "Ukraine War",       0.72),
]

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📅 Filter by Date")
    # FIX: min_value aur max_value set karo taake poora range selectable ho
    min_date = df["DATE"].min().date()
    max_date = df["DATE"].max().date()
    start_date = st.date_input("Start Date", min_date,
                               min_value=min_date, max_value=max_date)
    end_date   = st.date_input("End Date",   max_date,
                               min_value=min_date, max_value=max_date)
    st.markdown("---")
    st.markdown("**About VIX**")
    st.markdown("- **< 15** → Market is calm 🟢\n- **15–25** → Normal volatility 🔵\n- **25–35** → High fear 🟠\n- **> 35** → Extreme panic 🔴")

mask = (df["DATE"] >= pd.to_datetime(start_date)) & (df["DATE"] <= pd.to_datetime(end_date))
dff  = df.loc[mask].copy()

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<div class="main-title">📈 VIX Fear Index Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Interactive visualization of CBOE Volatility Index (1990–2026)</div>', unsafe_allow_html=True)

# ── Metrics ───────────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
def mcard(col, lbl, val, color):
    col.markdown(f"""<div class="metric-box">
        <div class="metric-lbl">{lbl}</div>
        <div class="metric-val" style="color:{color};">{val}</div>
    </div>""", unsafe_allow_html=True)

mcard(c1, "Current VIX",   f"{dff['CLOSE'].iloc[-1]:.2f}",  "#4C9BE8")
mcard(c2, "Average VIX",   f"{dff['CLOSE'].mean():.2f}",    "#f39c12")
mcard(c3, "All-Time High",  f"{df['CLOSE'].max():.2f}",     "#e74c3c")
mcard(c4, "All-Time Low",   f"{df['CLOSE'].min():.2f}",     "#2ecc71")

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# helper: base layout without xaxis/yaxis (to avoid conflict)
def base_layout(height=380):
    return dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#111111",
        font=dict(family="EB Garamond, Georgia, serif", color="#cccccc", size=12),
        margin=dict(l=55, r=30, t=35, b=50),
        height=height,
        legend=dict(bgcolor="rgba(20,20,20,0.85)", bordercolor="#333", borderwidth=1)
    )

GRID = dict(gridcolor="#222", showgrid=True, zeroline=False)

# ══ CHART 1 — VIX Trend ══════════════════════════════════════════════════════
st.markdown('<div class="chart-title">📊 Chart 1 — VIX Trend Over Time</div>', unsafe_allow_html=True)
st.markdown('<div class="chart-desc">Full historical VIX with major market crisis events marked</div>', unsafe_allow_html=True)

fig1 = go.Figure()
fig1.add_trace(go.Scatter(
    x=dff["DATE"], y=dff["CLOSE"], mode="lines", name="VIX Close",
    line=dict(color="#4C9BE8", width=1.0),
    fill="tozeroy", fillcolor="rgba(76,155,232,0.07)"
))
ymax = dff["CLOSE"].max() if len(dff) else 80
for date_str, label, yfrac in CRISES:
    cdate = pd.to_datetime(date_str)
    if pd.to_datetime(start_date) <= cdate <= pd.to_datetime(end_date):
        fig1.add_vline(x=cdate, line_dash="dash", line_color="rgba(231,76,60,0.55)", line_width=1.2)
        fig1.add_annotation(x=cdate, y=ymax*yfrac, text=f"<b>{label}</b>",
                            showarrow=False, font=dict(size=10, color="#e74c3c"),
                            bgcolor="rgba(18,18,18,0.78)", borderpad=3,
                            xanchor="left", yanchor="middle")
fig1.update_layout(**base_layout(390))
fig1.update_xaxes(title_text="Date", **GRID)
fig1.update_yaxes(title_text="VIX Close", **GRID)
st.plotly_chart(fig1, use_container_width=True)

# ══ CHART 2 — Moving Averages ════════════════════════════════════════════════
st.markdown('<div class="chart-title">📉 Chart 2 — Moving Averages (30-day vs 252-day)</div>', unsafe_allow_html=True)
st.markdown('<div class="chart-desc">Short-term (30-day) vs long-term (252-day ≈ 1 year) smoothed trend</div>', unsafe_allow_html=True)

fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=dff["DATE"], y=dff["CLOSE"],   name="VIX Daily",  line=dict(color="#4C9BE8", width=0.8), opacity=0.45))
fig2.add_trace(go.Scatter(x=dff["DATE"], y=dff["MA_30"],   name="30-day MA",  line=dict(color="#f39c12", width=2.0)))
fig2.add_trace(go.Scatter(x=dff["DATE"], y=dff["MA_252"],  name="252-day MA", line=dict(color="#e74c3c", width=2.2)))
fig2.update_layout(**base_layout(365))
fig2.update_xaxes(title_text="Date", **GRID)
fig2.update_yaxes(title_text="VIX", **GRID)
st.plotly_chart(fig2, use_container_width=True)

# ══ CHART 3 — Yearly Average (FIX: no xaxis/yaxis in update_layout) ══════════
st.markdown('<div class="chart-title">📅 Chart 3 — Yearly Average VIX</div>', unsafe_allow_html=True)
st.markdown('<div class="chart-desc">Which years were most volatile? Red = high fear, Green = calm</div>', unsafe_allow_html=True)

yearly = dff.groupby("Year")["CLOSE"].mean().reset_index()
yearly.columns = ["Year", "Avg VIX"]
fig3 = px.bar(yearly, x="Year", y="Avg VIX",
              color="Avg VIX", color_continuous_scale="RdYlGn_r",
              text=yearly["Avg VIX"].round(1))
fig3.update_traces(textposition="outside", textfont=dict(size=9))
fig3.update_layout(**base_layout(385), coloraxis_showscale=False, bargap=0.22)
fig3.update_xaxes(title_text="Year", tickmode="linear", dtick=2, **GRID)
fig3.update_yaxes(title_text="Average VIX", **GRID)
st.plotly_chart(fig3, use_container_width=True)

# ══ CHART 4 — Monthly Heatmap ════════════════════════════════════════════════
st.markdown('<div class="chart-title">🗓️ Chart 4 — Monthly Seasonality Heatmap</div>', unsafe_allow_html=True)
st.markdown('<div class="chart-desc">Each cell = average VIX for that Year × Month. Red = high fear, Green = calm</div>', unsafe_allow_html=True)

month_map = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",
             7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}
pivot = dff.pivot_table(values="CLOSE", index="Year", columns="Month", aggfunc="mean").round(1)
pivot.columns = [month_map[m] for m in pivot.columns]
fig4 = px.imshow(pivot, color_continuous_scale="RdYlGn_r",
                 aspect="auto", labels=dict(color="Avg VIX"), text_auto=".0f")
fig4.update_traces(textfont=dict(size=8))
fig4.update_layout(**base_layout(530), coloraxis_colorbar=dict(title="Avg VIX", thickness=12))
fig4.update_xaxes(title_text="Month", **GRID)
fig4.update_yaxes(title_text="Year",  **GRID)
st.plotly_chart(fig4, use_container_width=True)

# ══ CHART 5 — Distribution by Fear Zones ════════════════════════════════════
st.markdown('<div class="chart-title">📐 Chart 5 — VIX Distribution by Fear Zones</div>', unsafe_allow_html=True)
st.markdown('<div class="chart-desc">How often does VIX stay in each zone? Most days are calm (green/blue)</div>', unsafe_allow_html=True)

fig5 = px.histogram(dff, x="CLOSE", color="Zone", nbins=55,
                    color_discrete_map=ZONE_COLORS,
                    labels={"CLOSE": "VIX Value", "count": "Number of Days"},
                    category_orders={"Zone": ["Low (<15)", "Normal (15-25)", "High (25-35)", "Extreme (>35)"]})
fig5.update_layout(**base_layout(365), bargap=0.04)
fig5.update_xaxes(title_text="VIX Value", **GRID)
fig5.update_yaxes(title_text="Number of Days", **GRID)
st.plotly_chart(fig5, use_container_width=True)

# ══ CHART 6 — Top 20 Highest VIX Days (horizontal) ══════════════════════════
st.markdown('<div class="chart-title">🔥 Chart 6 — Top 20 Highest VIX Days (All Time)</div>', unsafe_allow_html=True)
st.markdown('<div class="chart-desc">Scariest days in market history — almost all from 2008 Crash & COVID-19</div>', unsafe_allow_html=True)

top20 = df.nlargest(20, "CLOSE").sort_values("CLOSE", ascending=True).copy()
top20["Label"] = top20["DATE"].dt.strftime("%d %b %Y")
fig6 = go.Figure(go.Bar(
    x=top20["CLOSE"], y=top20["Label"], orientation="h",
    marker=dict(color=top20["CLOSE"], colorscale="Reds", showscale=False),
    text=top20["CLOSE"].round(2), textposition="outside",
    textfont=dict(size=11, color="#cccccc"),
    hovertemplate="<b>%{y}</b><br>VIX: %{x:.2f}<extra></extra>"
))
fig6.update_layout(**base_layout(530))
fig6.update_xaxes(title_text="VIX Close Value", range=[0, top20["CLOSE"].max()*1.18], **GRID)
fig6.update_yaxes(title_text="", gridcolor="rgba(0,0,0,0)")
st.plotly_chart(fig6, use_container_width=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown('<hr class="divider">', unsafe_allow_html=True)
st.markdown('<div style="text-align:center;color:#444;font-size:0.82rem;">📌 Data: DataHub — CBOE VIX Daily (1990–2026) &nbsp;|&nbsp; EDA Project &nbsp;|&nbsp; Streamlit + Plotly</div>', unsafe_allow_html=True)
