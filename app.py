"""
app.py
------
VIX Fear Index Dashboard — Main Application
EDA Project | DataHub Finance VIX (ID: 70177628)
"""

import streamlit as st
import pandas as pd

from filters import load_and_prepare, render_sidebar_filters
from charts  import (
    chart_line_trend, chart_moving_avg, chart_yearly_bar,
    chart_heatmap, chart_histogram, chart_top20_bar,
    chart_pie_zones, chart_scatter,
    chart_boxplot_seaborn, chart_countplot_seaborn, chart_violin_seaborn
)

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="VIX Fear Index Dashboard",
                   layout="wide", page_icon="📈")

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=EB+Garamond:wght@400;600;700&display=swap" rel="stylesheet">
<style>
  html, body, [class*="css"], .stMarkdown, p, div, span, label {
      font-family: 'EB Garamond', Georgia, serif !important;
  }
  .main-title  { font-size:2.3rem; font-weight:700; margin-bottom:0.2rem; }
  .sub-title   { color:#888; font-size:0.95rem; margin-bottom:1.2rem; }
  .chart-title { font-size:1.15rem; font-weight:600; margin:1.6rem 0 0.2rem; color:#e0e0e0; }
  .chart-desc  { font-size:0.85rem; color:#777; margin-bottom:0.4rem; }
  .metric-box  { background:#13131f; border:1px solid #2a2a3d;
                 border-radius:10px; padding:1rem 1.2rem; text-align:center; }
  .metric-lbl  { font-size:0.75rem; color:#777; text-transform:uppercase; letter-spacing:0.08em; }
  .metric-val  { font-size:2rem; font-weight:700; margin-top:4px; }
  .section-tag { display:inline-block; font-size:0.75rem; font-weight:600;
                 background:#1e2a3a; color:#4C9BE8; border-radius:20px;
                 padding:2px 10px; margin-bottom:6px; letter-spacing:0.05em; }
  hr.divider   { border:none; border-top:1px solid #2a2a3d; margin:1.2rem 0; }
  /* Hide sidebar collapse button */
  [data-testid="collapsedControl"] { display:none !important; }
  section[data-testid="stSidebarCollapsedControl"] { display:none !important; }
</style>
""", unsafe_allow_html=True)

# ── Load Data ─────────────────────────────────────────────────────────────────
@st.cache_data
def get_data():
    return load_and_prepare("vix-daily.csv")

df = get_data()

# ── Sidebar Filters ───────────────────────────────────────────────────────────
dff, start_date, end_date = render_sidebar_filters(df)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<div class="main-title">📈 VIX Fear Index Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Interactive visualization of CBOE Volatility Index (1990–2026) | DataHub Dataset ID: 70177628</div>', unsafe_allow_html=True)

# ── Guard: empty data after filter ───────────────────────────────────────────
if dff.empty:
    st.warning("⚠️ No data matches current filters. Please adjust the filters in the sidebar.")
    st.stop()

# ── KPI Cards ─────────────────────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
def mcard(col, lbl, val, color):
    col.markdown(f"""<div class="metric-box">
        <div class="metric-lbl">{lbl}</div>
        <div class="metric-val" style="color:{color};">{val}</div>
    </div>""", unsafe_allow_html=True)

mcard(c1, "Total Records",  f"{len(dff):,}",                    "#8e7dff")
mcard(c2, "Current VIX",   f"{dff['CLOSE'].iloc[-1]:.2f}",      "#4C9BE8")
mcard(c3, "Average VIX",   f"{dff['CLOSE'].mean():.2f}",        "#f39c12")
mcard(c4, "All-Time High",  f"{df['CLOSE'].max():.2f}",         "#e74c3c")
mcard(c5, "All-Time Low",   f"{df['CLOSE'].min():.2f}",         "#2ecc71")

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# SECTION 1 — TREND ANALYSIS
# ════════════════════════════════════════════════════════════════════════════
st.markdown('<span class="section-tag">SECTION 1 — TREND ANALYSIS</span>', unsafe_allow_html=True)

st.markdown('<div class="chart-title">📊 Chart 1 — VIX Trend Over Time (Line + Area)</div>', unsafe_allow_html=True)
st.markdown('<div class="chart-desc">Full historical VIX with major market crisis events marked. Area fill shows magnitude.</div>', unsafe_allow_html=True)
st.plotly_chart(chart_line_trend(dff, start_date, end_date), use_container_width=True)

st.markdown('<div class="chart-title">📉 Chart 2 — Moving Averages (30-day vs 252-day)</div>', unsafe_allow_html=True)
st.markdown('<div class="chart-desc">Short-term (30-day) vs long-term (252-day ≈ 1 trading year) trend smoothing.</div>', unsafe_allow_html=True)
st.plotly_chart(chart_moving_avg(dff), use_container_width=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# SECTION 2 — DISTRIBUTION ANALYSIS
# ════════════════════════════════════════════════════════════════════════════
st.markdown('<span class="section-tag">SECTION 2 — DISTRIBUTION ANALYSIS</span>', unsafe_allow_html=True)

col_a, col_b = st.columns(2)

with col_a:
    st.markdown('<div class="chart-title">🥧 Chart 3 — Fear Zone Distribution (Pie)</div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-desc">What % of days fall in each VIX fear zone?</div>', unsafe_allow_html=True)
    st.plotly_chart(chart_pie_zones(dff), use_container_width=True)

with col_b:
    st.markdown('<div class="chart-title">📐 Chart 4 — VIX Histogram by Fear Zones</div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-desc">Frequency distribution of daily VIX values, colored by zone.</div>', unsafe_allow_html=True)
    st.plotly_chart(chart_histogram(dff), use_container_width=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# SECTION 3 — SEABORN CHARTS (Mandatory)
# ════════════════════════════════════════════════════════════════════════════
st.markdown('<span class="section-tag">SECTION 3 — STATISTICAL ANALYSIS (Matplotlib + Seaborn)</span>', unsafe_allow_html=True)

st.markdown('<div class="chart-title">📦 Chart 5 — VIX Box Plot by Decade (Seaborn)</div>', unsafe_allow_html=True)
st.markdown('<div class="chart-desc">Spread, median, and outliers of VIX per decade. Dots = extreme outlier days.</div>', unsafe_allow_html=True)
st.pyplot(chart_boxplot_seaborn(dff), use_container_width=True)

col_c, col_d = st.columns(2)

with col_c:
    st.markdown('<div class="chart-title">🔢 Chart 6 — Count Plot by Zone (Seaborn)</div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-desc">How many trading days fall in each fear zone?</div>', unsafe_allow_html=True)
    st.pyplot(chart_countplot_seaborn(dff), use_container_width=True)

with col_d:
    st.markdown('<div class="chart-title">🎻 Chart 7 — Violin Plot by Decade (Seaborn)</div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-desc">Probability density + quartiles of VIX for each decade.</div>', unsafe_allow_html=True)
    st.pyplot(chart_violin_seaborn(dff), use_container_width=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# SECTION 4 — COMPARATIVE ANALYSIS
# ════════════════════════════════════════════════════════════════════════════
st.markdown('<span class="section-tag">SECTION 4 — COMPARATIVE ANALYSIS</span>', unsafe_allow_html=True)

st.markdown('<div class="chart-title">📅 Chart 8 — Yearly Average VIX (Bar)</div>', unsafe_allow_html=True)
st.markdown('<div class="chart-desc">Which years were most volatile? Red = high fear, Green = calm market.</div>', unsafe_allow_html=True)
st.plotly_chart(chart_yearly_bar(dff), use_container_width=True)

st.markdown('<div class="chart-title">🔵 Chart 9 — VIX Open vs Close (Scatter)</div>', unsafe_allow_html=True)
st.markdown('<div class="chart-desc">Relationship between daily Open and Close VIX. Points above dashed line = closed higher than opened.</div>', unsafe_allow_html=True)
st.plotly_chart(chart_scatter(dff), use_container_width=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# SECTION 5 — SEASONALITY & EXTREMES
# ════════════════════════════════════════════════════════════════════════════
st.markdown('<span class="section-tag">SECTION 5 — SEASONALITY & EXTREMES</span>', unsafe_allow_html=True)

st.markdown('<div class="chart-title">🗓️ Chart 10 — Monthly Seasonality Heatmap</div>', unsafe_allow_html=True)
st.markdown('<div class="chart-desc">Average VIX per Year × Month. Red = high fear. Spot which months are historically volatile.</div>', unsafe_allow_html=True)
st.plotly_chart(chart_heatmap(dff), use_container_width=True)

st.markdown('<div class="chart-title">🔥 Chart 11 — Top 20 Highest VIX Days (All Time)</div>', unsafe_allow_html=True)
st.markdown('<div class="chart-desc">The most fearful trading days in history. Almost all from 2008 Crash & COVID-19.</div>', unsafe_allow_html=True)
st.plotly_chart(chart_top20_bar(dff), use_container_width=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown('<hr class="divider">', unsafe_allow_html=True)
st.markdown(
    '<div style="text-align:center;color:#444;font-size:0.82rem;">'
    '📌 Data Source: DataHub — CBOE VIX Daily (1990–2026) &nbsp;|&nbsp; '
    'EDA Project &nbsp;|&nbsp; Built with Streamlit, Plotly, Matplotlib & Seaborn'
    '</div>',
    unsafe_allow_html=True
)
