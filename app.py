import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="VIX Fear Index Dashboard", layout="wide")

st.title("📈 VIX Fear Index Dashboard")
st.markdown("Interactive visualization of CBOE Volatility Index (1990–2026)")

# ── Load Data ────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("vix-daily-cleaned.csv")
    df["DATE"] = pd.to_datetime(df["DATE"])
    df["MA_30"]  = df["CLOSE"].rolling(window=30).mean()
    df["MA_252"] = df["CLOSE"].rolling(window=252).mean()
    df["Year"]  = df["DATE"].dt.year
    df["Month"] = df["DATE"].dt.month
    df["Zone"]  = pd.cut(
        df["CLOSE"],
        bins=[0, 15, 25, 35, 999],
        labels=["Low (<15)", "Normal (15–25)", "High (25–35)", "Extreme (>35)"]
    )
    return df

df = load_data()

# ── Sidebar Date Filter ───────────────────────────────────────────────────────
st.sidebar.header("📅 Filter by Date")
start_date = st.sidebar.date_input("Start Date", df["DATE"].min().date())
end_date   = st.sidebar.date_input("End Date",   df["DATE"].max().date())

mask = (df["DATE"] >= pd.to_datetime(start_date)) & (df["DATE"] <= pd.to_datetime(end_date))
dff = df.loc[mask].copy()

# ── Crisis Events (for annotations) ─────────────────────────────────────────
crises = [
    {"date": "1997-10-27", "label": "Asian Crisis"},
    {"date": "2001-09-11", "label": "9/11"},
    {"date": "2008-10-24", "label": "2008 Crash"},
    {"date": "2010-05-06", "label": "Flash Crash"},
    {"date": "2020-03-16", "label": "COVID Peak"},
    {"date": "2022-03-07", "label": "Ukraine War"},
]

# ── Top Metrics ───────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.metric("Current VIX",       f"{dff['CLOSE'].iloc[-1]:.2f}")
c2.metric("Average VIX",       f"{dff['CLOSE'].mean():.2f}")
c3.metric("Max VIX",           f"{dff['CLOSE'].max():.2f}")
c4.metric("Min VIX",           f"{dff['CLOSE'].min():.2f}")

st.divider()

# ── Chart 1: VIX Trend with Crisis Annotations ───────────────────────────────
st.subheader("📊 Chart 1 — VIX Trend Over Time (with Crisis Events)")
fig1 = go.Figure()
fig1.add_trace(go.Scatter(
    x=dff["DATE"], y=dff["CLOSE"],
    mode="lines", name="VIX Close",
    line=dict(color="#4C9BE8", width=1.2)
))
# Add crisis vertical lines
for c in crises:
    cdate = pd.to_datetime(c["date"])
    if pd.to_datetime(start_date) <= cdate <= pd.to_datetime(end_date):
        fig1.add_vline(x=cdate, line_dash="dot", line_color="red", line_width=1)
        fig1.add_annotation(x=cdate, y=dff["CLOSE"].max()*0.95,
                            text=c["label"], showarrow=False,
                            font=dict(size=10, color="red"), textangle=-90)
fig1.update_layout(height=420, xaxis_title="Date", yaxis_title="VIX")
st.plotly_chart(fig1, use_container_width=True)

# ── Chart 2: Moving Averages ─────────────────────────────────────────────────
st.subheader("📉 Chart 2 — Moving Averages (30-day vs 252-day)")
fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=dff["DATE"], y=dff["CLOSE"],   name="VIX",       line=dict(color="#4C9BE8", width=1)))
fig2.add_trace(go.Scatter(x=dff["DATE"], y=dff["MA_30"],   name="30-day MA",  line=dict(color="orange",  width=1.8)))
fig2.add_trace(go.Scatter(x=dff["DATE"], y=dff["MA_252"],  name="252-day MA", line=dict(color="red",     width=2)))
fig2.update_layout(height=380, xaxis_title="Date", yaxis_title="VIX")
st.plotly_chart(fig2, use_container_width=True)

# ── Chart 3: Yearly Average Bar ───────────────────────────────────────────────
st.subheader("📅 Chart 3 — Yearly Average VIX")
yearly = dff.groupby("Year")["CLOSE"].mean().reset_index()
fig3 = px.bar(yearly, x="Year", y="CLOSE",
              labels={"CLOSE": "Average VIX"},
              color="CLOSE", color_continuous_scale="RdYlGn_r",
              height=380)
fig3.update_layout(coloraxis_showscale=False)
st.plotly_chart(fig3, use_container_width=True)

# ── Chart 4: Monthly Heatmap ─────────────────────────────────────────────────
st.subheader("🗓️ Chart 4 — Monthly Seasonality Heatmap")
month_names = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",
               7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}
pivot = dff.pivot_table(values="CLOSE", index="Year", columns="Month", aggfunc="mean")
pivot.columns = [month_names[m] for m in pivot.columns]
fig4 = px.imshow(pivot,
                 color_continuous_scale="RdYlGn_r",
                 aspect="auto", height=500,
                 labels=dict(color="Avg VIX"))
fig4.update_layout(xaxis_title="Month", yaxis_title="Year")
st.plotly_chart(fig4, use_container_width=True)

# ── Chart 5: VIX Distribution by Fear Zones ──────────────────────────────────
st.subheader("📐 Chart 5 — VIX Distribution by Fear Zones")
zone_colors = {
    "Low (<15)":      "green",
    "Normal (15–25)": "steelblue",
    "High (25–35)":   "orange",
    "Extreme (>35)":  "red"
}
fig5 = px.histogram(dff, x="CLOSE", color="Zone", nbins=60,
                    color_discrete_map=zone_colors,
                    labels={"CLOSE": "VIX Value"},
                    height=380)
fig5.update_layout(bargap=0.05)
st.plotly_chart(fig5, use_container_width=True)

# ── Chart 6: Top 20 Highest VIX Days ─────────────────────────────────────────
st.subheader("🔥 Chart 6 — Top 20 Highest VIX Days (All Time)")
top20 = df.nlargest(20, "CLOSE").sort_values("CLOSE", ascending=False)
top20["DATE_STR"] = top20["DATE"].dt.strftime("%Y-%m-%d")
fig6 = px.bar(top20, x="DATE_STR", y="CLOSE",
              color="CLOSE", color_continuous_scale="Reds",
              labels={"DATE_STR": "Date", "CLOSE": "VIX Close"},
              height=400)
fig6.update_layout(xaxis_tickangle=-45, coloraxis_showscale=False)
st.plotly_chart(fig6, use_container_width=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.divider()
st.caption("📌 Data Source: DataHub — CBOE VIX Daily (1990–2026) | EDA Project")
