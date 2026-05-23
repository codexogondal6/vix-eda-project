import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ── Google Font: George ───────────────────────────────────────────────────────
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Geo:ital@0;1&display=swap" rel="stylesheet">
<style>
    html, body, [class*="css"], .stMarkdown, .stMetric, h1, h2, h3, p, div {
        font-family: 'Georgia', 'Times New Roman', serif !important;
    }
    .main-title {
        font-family: 'Georgia', serif !important;
        font-size: 2.4rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }
    .section-divider {
        border: none;
        border-top: 1px solid #333;
        margin: 1.5rem 0;
    }
    .metric-container {
        background: #1a1a2e;
        border: 1px solid #2d2d44;
        border-radius: 10px;
        padding: 1rem 1.5rem;
        text-align: center;
    }
    .metric-label {
        font-size: 0.8rem;
        color: #888;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 4px;
        font-family: 'Georgia', serif !important;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #4C9BE8;
        font-family: 'Georgia', serif !important;
    }
    .chart-title {
        font-size: 1.15rem;
        font-weight: 600;
        margin: 1.5rem 0 0.3rem 0;
        color: #e0e0e0;
        font-family: 'Georgia', serif !important;
    }
    .chart-desc {
        font-size: 0.82rem;
        color: #888;
        margin-bottom: 0.5rem;
        font-family: 'Georgia', serif !important;
    }
</style>
""", unsafe_allow_html=True)

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="VIX Fear Index Dashboard", layout="wide", page_icon="📈")

# ── Load & Prepare Data ───────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("vix-daily-cleaned.csv")
    df["DATE"]   = pd.to_datetime(df["DATE"])
    df["MA_30"]  = df["CLOSE"].rolling(30).mean()
    df["MA_252"] = df["CLOSE"].rolling(252).mean()
    df["Year"]   = df["DATE"].dt.year
    df["Month"]  = df["DATE"].dt.month
    df["Zone"]   = pd.cut(df["CLOSE"],
                          bins=[0, 15, 25, 35, 9999],
                          labels=["Low (<15)", "Normal (15–25)", "High (25–35)", "Extreme (>35)"])
    return df

df = load_data()

ZONE_COLORS = {
    "Low (<15)":      "#2ecc71",
    "Normal (15–25)": "#3498db",
    "High (25–35)":   "#e67e22",
    "Extreme (>35)":  "#e74c3c"
}

PLOT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="#111111",
    font=dict(family="Georgia, serif", color="#cccccc", size=12),
    margin=dict(l=50, r=30, t=40, b=50),
    xaxis=dict(gridcolor="#222", showgrid=True, zeroline=False),
    yaxis=dict(gridcolor="#222", showgrid=True, zeroline=False),
)

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
    start_date = st.date_input("Start Date", df["DATE"].min().date())
    end_date   = st.date_input("End Date",   df["DATE"].max().date())
    st.markdown("---")
    st.markdown("**About VIX**")
    st.markdown("""
    - **< 15** → Market is calm 🟢  
    - **15–25** → Normal volatility 🔵  
    - **25–35** → High fear 🟠  
    - **> 35** → Extreme panic 🔴  
    """)

mask = (df["DATE"] >= pd.to_datetime(start_date)) & (df["DATE"] <= pd.to_datetime(end_date))
dff  = df.loc[mask].copy()

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<div class="main-title">📈 VIX Fear Index Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div style="color:#888; font-size:0.9rem; margin-bottom:1.2rem; font-family:Georgia,serif;">Interactive visualization of CBOE Volatility Index (1990–2026)</div>', unsafe_allow_html=True)

# ── Metrics ───────────────────────────────────────────────────────────────────
m1, m2, m3, m4 = st.columns(4)
def metric_card(col, label, value, color="#4C9BE8"):
    col.markdown(f"""
    <div class="metric-container">
        <div class="metric-label">{label}</div>
        <div class="metric-value" style="color:{color};">{value}</div>
    </div>""", unsafe_allow_html=True)

metric_card(m1, "Current VIX",  f"{dff['CLOSE'].iloc[-1]:.2f}",  "#4C9BE8")
metric_card(m2, "Average VIX",  f"{dff['CLOSE'].mean():.2f}",    "#f39c12")
metric_card(m3, "All-Time High",f"{df['CLOSE'].max():.2f}",      "#e74c3c")
metric_card(m4, "All-Time Low", f"{df['CLOSE'].min():.2f}",      "#2ecc71")

st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# CHART 1 — VIX Trend with Crisis Annotations
# ══════════════════════════════════════════════════════════════════
st.markdown('<div class="chart-title">📊 Chart 1 — VIX Trend Over Time</div>', unsafe_allow_html=True)
st.markdown('<div class="chart-desc">Full historical VIX with major market crisis events marked</div>', unsafe_allow_html=True)

fig1 = go.Figure()
fig1.add_trace(go.Scatter(
    x=dff["DATE"], y=dff["CLOSE"],
    mode="lines", name="VIX Close",
    line=dict(color="#4C9BE8", width=1.0),
    fill="tozeroy", fillcolor="rgba(76,155,232,0.08)"
))

ymax = dff["CLOSE"].max()
for date_str, label, y_frac in CRISES:
    cdate = pd.to_datetime(date_str)
    if pd.to_datetime(start_date) <= cdate <= pd.to_datetime(end_date):
        fig1.add_vline(x=cdate, line_dash="dash", line_color="rgba(231,76,60,0.6)", line_width=1.2)
        fig1.add_annotation(
            x=cdate, y=ymax * y_frac,
            text=f"<b>{label}</b>",
            showarrow=False,
            font=dict(size=10, color="#e74c3c", family="Georgia, serif"),
            bgcolor="rgba(20,20,20,0.75)",
            borderpad=3,
            xanchor="left", yanchor="middle"
        )

fig1.update_layout(**PLOT_LAYOUT, height=380,
                   xaxis_title="Date", yaxis_title="VIX Close",
                   legend=dict(bgcolor="rgba(0,0,0,0)"))
st.plotly_chart(fig1, use_container_width=True)

# ══════════════════════════════════════════════════════════════════
# CHART 2 — Moving Averages
# ══════════════════════════════════════════════════════════════════
st.markdown('<div class="chart-title">📉 Chart 2 — Moving Averages (30-day vs 252-day)</div>', unsafe_allow_html=True)
st.markdown('<div class="chart-desc">Short-term (30-day) and long-term (252-day ≈ 1 year) smoothed trends</div>', unsafe_allow_html=True)

fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=dff["DATE"], y=dff["CLOSE"],  name="VIX Daily",   line=dict(color="#4C9BE8", width=0.8), opacity=0.5))
fig2.add_trace(go.Scatter(x=dff["DATE"], y=dff["MA_30"],  name="30-day MA",   line=dict(color="#f39c12", width=2.0)))
fig2.add_trace(go.Scatter(x=dff["DATE"], y=dff["MA_252"], name="252-day MA",  line=dict(color="#e74c3c", width=2.2)))
fig2.update_layout(**PLOT_LAYOUT, height=360,
                   xaxis_title="Date", yaxis_title="VIX",
                   legend=dict(bgcolor="rgba(20,20,20,0.8)", bordercolor="#333", borderwidth=1))
st.plotly_chart(fig2, use_container_width=True)

# ══════════════════════════════════════════════════════════════════
# CHART 3 — Yearly Average
# ══════════════════════════════════════════════════════════════════
st.markdown('<div class="chart-title">📅 Chart 3 — Yearly Average VIX</div>', unsafe_allow_html=True)
st.markdown('<div class="chart-desc">Which years were the most volatile? Red = high fear, Green = calm market</div>', unsafe_allow_html=True)

yearly = dff.groupby("Year")["CLOSE"].mean().reset_index()
yearly.columns = ["Year", "Avg VIX"]
fig3 = px.bar(yearly, x="Year", y="Avg VIX",
              color="Avg VIX", color_continuous_scale="RdYlGn_r",
              text=yearly["Avg VIX"].round(1))
fig3.update_traces(textposition="outside", textfont=dict(size=9, family="Georgia, serif"))
fig3.update_layout(**PLOT_LAYOUT, height=380,
                   coloraxis_showscale=False,
                   bargap=0.25,
                   xaxis=dict(tickmode="linear", dtick=2, gridcolor="#222"),
                   yaxis=dict(gridcolor="#222"))
st.plotly_chart(fig3, use_container_width=True)

# ══════════════════════════════════════════════════════════════════
# CHART 4 — Monthly Heatmap
# ══════════════════════════════════════════════════════════════════
st.markdown('<div class="chart-title">🗓️ Chart 4 — Monthly Seasonality Heatmap</div>', unsafe_allow_html=True)
st.markdown('<div class="chart-desc">Each cell = average VIX for that Year × Month. Red = high fear, Green = calm</div>', unsafe_allow_html=True)

month_map = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",
             7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}
pivot = dff.pivot_table(values="CLOSE", index="Year", columns="Month", aggfunc="mean").round(1)
pivot.columns = [month_map[m] for m in pivot.columns]

fig4 = px.imshow(pivot,
                 color_continuous_scale="RdYlGn_r",
                 aspect="auto",
                 labels=dict(color="Avg VIX"),
                 text_auto=".0f")
fig4.update_traces(textfont=dict(size=8, family="Georgia, serif"))
fig4.update_layout(**PLOT_LAYOUT, height=520,
                   xaxis_title="Month", yaxis_title="Year",
                   coloraxis_colorbar=dict(title="Avg VIX", thickness=12))
st.plotly_chart(fig4, use_container_width=True)

# ══════════════════════════════════════════════════════════════════
# CHART 5 — VIX Distribution by Fear Zones
# ══════════════════════════════════════════════════════════════════
st.markdown('<div class="chart-title">📐 Chart 5 — VIX Distribution by Fear Zones</div>', unsafe_allow_html=True)
st.markdown('<div class="chart-desc">How often does VIX stay in each zone? Most days are calm (green/blue)</div>', unsafe_allow_html=True)

fig5 = px.histogram(dff, x="CLOSE", color="Zone", nbins=55,
                    color_discrete_map=ZONE_COLORS,
                    labels={"CLOSE": "VIX Value", "count": "Number of Days"},
                    category_orders={"Zone": ["Low (<15)", "Normal (15–25)", "High (25–35)", "Extreme (>35)"]})
fig5.update_layout(**PLOT_LAYOUT, height=360,
                   bargap=0.04,
                   xaxis_title="VIX Value", yaxis_title="Number of Days",
                   legend=dict(title="Fear Zone", bgcolor="rgba(20,20,20,0.8)",
                               bordercolor="#333", borderwidth=1))
st.plotly_chart(fig5, use_container_width=True)

# ══════════════════════════════════════════════════════════════════
# CHART 6 — Top 20 Highest VIX Days (FIXED — horizontal bar)
# ══════════════════════════════════════════════════════════════════
st.markdown('<div class="chart-title">🔥 Chart 6 — Top 20 Highest VIX Days (All Time)</div>', unsafe_allow_html=True)
st.markdown('<div class="chart-desc">The scariest days in market history — almost all from 2008 crash & COVID-19</div>', unsafe_allow_html=True)

top20 = df.nlargest(20, "CLOSE").sort_values("CLOSE", ascending=True).copy()
top20["Label"] = top20["DATE"].dt.strftime("%d %b %Y")

fig6 = go.Figure(go.Bar(
    x=top20["CLOSE"],
    y=top20["Label"],
    orientation="h",
    marker=dict(
        color=top20["CLOSE"],
        colorscale="Reds",
        showscale=False
    ),
    text=top20["CLOSE"].round(2),
    textposition="outside",
    textfont=dict(size=11, family="Georgia, serif", color="#cccccc"),
    hovertemplate="<b>%{y}</b><br>VIX: %{x:.2f}<extra></extra>"
))
fig6.update_layout(**PLOT_LAYOUT, height=520,
                   xaxis_title="VIX Close Value",
                   yaxis_title="",
                   xaxis=dict(range=[0, top20["CLOSE"].max() * 1.15], gridcolor="#222"),
                   yaxis=dict(gridcolor="rgba(0,0,0,0)"))
st.plotly_chart(fig6, use_container_width=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
st.markdown('<div style="text-align:center; color:#555; font-size:0.8rem; font-family:Georgia,serif;">📌 Data Source: DataHub — CBOE VIX Daily (1990–2026) &nbsp;|&nbsp; EDA Project &nbsp;|&nbsp; Built with Streamlit & Plotly</div>', unsafe_allow_html=True)
