"""
charts.py
---------
All chart/visualization functions for VIX Dashboard.
Uses: Plotly (interactive), Matplotlib & Seaborn (static — mandatory by sir).
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ── Shared Style ──────────────────────────────────────────────────────────────
ZONE_COLORS = {
    "Low (<15)":      "#2ecc71",
    "Normal (15-25)": "#3498db",
    "High (25-35)":   "#e67e22",
    "Extreme (>35)":  "#e74c3c"
}

CRISES = [
    ("1997-10-27", "Asian Crisis '97"),
    ("2001-09-11", "9/11 Attack"),
    ("2008-10-24", "2008 Crash"),
    ("2010-05-06", "Flash Crash '10"),
    ("2020-03-16", "COVID-19 Peak"),
    ("2022-03-07", "Ukraine War"),
]

FONT = "EB Garamond, Georgia, serif"

def _base(height=380):
    return dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#0f0f1a",
        font=dict(family=FONT, color="#cccccc", size=12),
        margin=dict(l=55, r=30, t=40, b=50),
        height=height,
        legend=dict(bgcolor="rgba(20,20,20,0.85)", bordercolor="#333", borderwidth=1)
    )

GRID = dict(gridcolor="#222", showgrid=True, zeroline=False)

# ═════════════════════════════════════════════════════════════════════════════
# PLOTLY CHARTS (Interactive)
# ═════════════════════════════════════════════════════════════════════════════

def chart_line_trend(dff, start_date, end_date):
    """Chart 1 — Line/Area: VIX Trend Over Time with Crisis Annotations."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dff["DATE"], y=dff["CLOSE"], mode="lines", name="VIX Close",
        line=dict(color="#4C9BE8", width=1.0),
        fill="tozeroy", fillcolor="rgba(76,155,232,0.07)"
    ))
    ymax = dff["CLOSE"].max() if len(dff) else 80
    for date_str, label in CRISES:
        cdate = pd.to_datetime(date_str)
        if pd.to_datetime(start_date) <= cdate <= pd.to_datetime(end_date):
            fig.add_vline(x=cdate, line_dash="dash",
                          line_color="rgba(231,76,60,0.55)", line_width=1.2)
            fig.add_annotation(x=cdate, y=ymax * 0.92, text=f"<b>{label}</b>",
                               showarrow=False, font=dict(size=10, color="#e74c3c"),
                               bgcolor="rgba(18,18,18,0.78)", borderpad=3,
                               xanchor="left", yanchor="middle")
    fig.update_layout(**_base(390))
    fig.update_xaxes(title_text="Date", **GRID)
    fig.update_yaxes(title_text="VIX Close", **GRID)
    return fig


def chart_moving_avg(dff):
    """Chart 2 — Line: Moving Averages (30-day vs 252-day)."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dff["DATE"], y=dff["CLOSE"],
                             name="VIX Daily", line=dict(color="#4C9BE8", width=0.8), opacity=0.4))
    fig.add_trace(go.Scatter(x=dff["DATE"], y=dff["MA_30"],
                             name="30-day MA", line=dict(color="#f39c12", width=2.0)))
    fig.add_trace(go.Scatter(x=dff["DATE"], y=dff["MA_252"],
                             name="252-day MA", line=dict(color="#e74c3c", width=2.2)))
    fig.update_layout(**_base(365))
    fig.update_xaxes(title_text="Date", **GRID)
    fig.update_yaxes(title_text="VIX", **GRID)
    return fig


def chart_yearly_bar(dff):
    """Chart 3 — Bar: Yearly Average VIX."""
    yearly = dff.groupby("Year")["CLOSE"].mean().reset_index()
    yearly.columns = ["Year", "Avg VIX"]
    fig = px.bar(yearly, x="Year", y="Avg VIX",
                 color="Avg VIX", color_continuous_scale="RdYlGn_r",
                 text=yearly["Avg VIX"].round(1))
    fig.update_traces(textposition="outside", textfont=dict(size=9))
    fig.update_layout(**_base(385), coloraxis_showscale=False, bargap=0.22)
    fig.update_xaxes(title_text="Year", tickmode="linear", dtick=2, **GRID)
    fig.update_yaxes(title_text="Average VIX", **GRID)
    return fig


def chart_heatmap(dff):
    """Chart 4 — Heatmap: Monthly Seasonality."""
    month_map = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",
                 7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}
    pivot = dff.pivot_table(values="CLOSE", index="Year", columns="Month", aggfunc="mean").round(1)
    pivot.columns = [month_map[m] for m in pivot.columns]
    fig = px.imshow(pivot, color_continuous_scale="RdYlGn_r",
                    aspect="auto", labels=dict(color="Avg VIX"), text_auto=".0f")
    fig.update_traces(textfont=dict(size=8))
    fig.update_layout(**_base(530), coloraxis_colorbar=dict(title="Avg VIX", thickness=12))
    fig.update_xaxes(title_text="Month", **GRID)
    fig.update_yaxes(title_text="Year", **GRID)
    return fig


def chart_histogram(dff):
    """Chart 5 — Histogram: VIX Distribution by Fear Zones."""
    fig = px.histogram(dff, x="CLOSE", color="Zone", nbins=55,
                       color_discrete_map=ZONE_COLORS,
                       labels={"CLOSE": "VIX Value", "count": "Number of Days"},
                       category_orders={"Zone": list(ZONE_COLORS.keys())})
    fig.update_layout(**_base(365), bargap=0.04)
    fig.update_xaxes(title_text="VIX Value", **GRID)
    fig.update_yaxes(title_text="Number of Days", **GRID)
    return fig


def chart_top20_bar(df_full):
    """Chart 6 — Horizontal Bar: Top 20 Highest VIX Days (always from full data)."""
    top20 = df_full.nlargest(20, "CLOSE").sort_values("CLOSE", ascending=True).copy()
    top20["Label"] = top20["DATE"].dt.strftime("%d %b %Y")
    fig = go.Figure(go.Bar(
        x=top20["CLOSE"], y=top20["Label"], orientation="h",
        marker=dict(color=top20["CLOSE"], colorscale="Reds", showscale=False),
        text=top20["CLOSE"].round(2), textposition="outside",
        textfont=dict(size=11, color="#cccccc"),
        hovertemplate="<b>%{y}</b><br>VIX: %{x:.2f}<extra></extra>"
    ))
    fig.update_layout(**_base(530))
    fig.update_xaxes(title_text="VIX Close Value",
                     range=[0, top20["CLOSE"].max() * 1.18], **GRID)
    fig.update_yaxes(title_text="", gridcolor="rgba(0,0,0,0)")
    return fig


def chart_pie_zones(dff):
    """Chart 7 — Pie: Proportional distribution of VIX Fear Zones."""
    zone_counts = dff["Zone"].value_counts().reset_index()
    zone_counts.columns = ["Zone", "Days"]
    fig = px.pie(zone_counts, names="Zone", values="Days",
                 color="Zone", color_discrete_map=ZONE_COLORS,
                 hole=0.38)
    fig.update_traces(textposition="outside", textinfo="percent+label",
                      textfont=dict(size=12))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#0f0f1a",
        font=dict(family=FONT, color="#cccccc", size=12),
        margin=dict(l=55, r=30, t=40, b=50),
        height=400,
        showlegend=True,
        legend=dict(orientation="v", x=1.02, y=0.5,
                    bgcolor="rgba(20,20,20,0.85)",
                    bordercolor="#333", borderwidth=1)
    )
    return fig


def chart_scatter(dff):
    """Chart 8 — Scatter: OPEN vs CLOSE colored by Zone."""
    fig = px.scatter(dff, x="OPEN", y="CLOSE", color="Zone",
                     color_discrete_map=ZONE_COLORS,
                     opacity=0.55,
                     labels={"OPEN": "VIX Open", "CLOSE": "VIX Close"},
                     category_orders={"Zone": list(ZONE_COLORS.keys())})
    # Add diagonal reference line
    vmin = dff[["OPEN","CLOSE"]].min().min()
    vmax = dff[["OPEN","CLOSE"]].max().max()
    fig.add_trace(go.Scatter(x=[vmin, vmax], y=[vmin, vmax],
                             mode="lines", name="Open = Close",
                             line=dict(color="white", dash="dash", width=1),
                             showlegend=True))
    fig.update_layout(**_base(400))
    fig.update_xaxes(title_text="VIX Open", **GRID)
    fig.update_yaxes(title_text="VIX Close", **GRID)
    return fig


# ═════════════════════════════════════════════════════════════════════════════
# MATPLOTLIB + SEABORN CHARTS (Mandatory by Sir)
# ═════════════════════════════════════════════════════════════════════════════

def _dark_style():
    plt.style.use("dark_background")
    plt.rcParams.update({
        "font.family":    "DejaVu Serif",
        "axes.facecolor": "#0f0f1a",
        "figure.facecolor":"#0a0a14",
        "axes.edgecolor": "#333",
        "grid.color":     "#222",
        "text.color":     "#cccccc",
        "axes.labelcolor":"#cccccc",
        "xtick.color":    "#cccccc",
        "ytick.color":    "#cccccc",
    })


def chart_boxplot_seaborn(dff):
    """Chart 9 — Box Plot (Seaborn): VIX distribution by Year decade."""
    _dark_style()
    fig, ax = plt.subplots(figsize=(12, 5))
    palette = {"1990s":"#3498db","2000s":"#e67e22","2010s":"#2ecc71","2020s":"#e74c3c"}
    order = [d for d in ["1990s","2000s","2010s","2020s"] if d in dff["Decade"].values]
    sns.boxplot(data=dff, x="Decade", y="CLOSE", palette=palette,
                order=order, width=0.5, linewidth=1.2,
                flierprops=dict(marker="o", markersize=2,
                                markerfacecolor="#e74c3c", alpha=0.4), ax=ax)
    ax.set_title("VIX Distribution by Decade — Box Plot", fontsize=14, pad=12)
    ax.set_xlabel("Decade", fontsize=11)
    ax.set_ylabel("VIX Close", fontsize=11)
    ax.grid(axis="y", alpha=0.3)
    ax.axhline(25, color="#e67e22", linestyle="--", linewidth=1, alpha=0.7, label="High Fear (25)")
    ax.axhline(35, color="#e74c3c", linestyle="--", linewidth=1, alpha=0.7, label="Extreme (35)")
    ax.legend(fontsize=9)
    plt.tight_layout()
    return fig


def chart_countplot_seaborn(dff):
    """Chart 10 — Count Plot (Seaborn): Number of days in each Fear Zone."""
    _dark_style()
    fig, ax = plt.subplots(figsize=(9, 5))
    zone_order = ["Low (<15)", "Normal (15-25)", "High (25-35)", "Extreme (>35)"]
    zone_pal   = [ZONE_COLORS[z] for z in zone_order if z in dff["Zone"].cat.categories]
    sns.countplot(data=dff, x="Zone", order=zone_order,
                  palette=zone_pal, ax=ax, width=0.55)
    # Add count labels on bars
    for p in ax.patches:
        h = p.get_height()
        if h > 0:
            ax.annotate(f"{int(h):,}",
                        xy=(p.get_x() + p.get_width() / 2, h),
                        xytext=(0, 5), textcoords="offset points",
                        ha="center", va="bottom", fontsize=11, color="#cccccc")
    ax.set_title("Number of Trading Days per Fear Zone — Count Plot", fontsize=14, pad=12)
    ax.set_xlabel("Fear Zone", fontsize=11)
    ax.set_ylabel("Number of Days", fontsize=11)
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    return fig


def chart_violin_seaborn(dff):
    """Chart 11 — Violin Plot (Seaborn): VIX distribution by Decade."""
    _dark_style()
    fig, ax = plt.subplots(figsize=(12, 5))
    palette = {"1990s":"#3498db","2000s":"#e67e22","2010s":"#2ecc71","2020s":"#e74c3c"}
    order = [d for d in ["1990s","2000s","2010s","2020s"] if d in dff["Decade"].values]
    sns.violinplot(data=dff, x="Decade", y="CLOSE", palette=palette,
                   order=order, inner="quartile", linewidth=1.2, ax=ax)
    ax.set_title("VIX Probability Distribution by Decade — Violin Plot", fontsize=14, pad=12)
    ax.set_xlabel("Decade", fontsize=11)
    ax.set_ylabel("VIX Close", fontsize=11)
    ax.grid(axis="y", alpha=0.3)
    ax.axhline(19.45, color="white", linestyle="--",
               linewidth=1, alpha=0.6, label="Overall Mean (19.45)")
    ax.legend(fontsize=9)
    plt.tight_layout()
    return fig
def chart_bubble(dff):
    """Bonus — Bubble Chart: Year vs Avg VIX, bubble size = Max VIX"""
    yearly = dff.groupby("Year").agg(
        Avg_VIX=("CLOSE","mean"),
        Max_VIX=("CLOSE","max"),
        Count=("CLOSE","count")
    ).reset_index()
    fig = px.scatter(yearly, x="Year", y="Avg_VIX",
                     size="Max_VIX", color="Avg_VIX",
                     color_continuous_scale="RdYlGn_r",
                     hover_data=["Max_VIX","Count"],
                     labels={"Avg_VIX":"Average VIX","Max_VIX":"Max VIX"},
                     size_max=55)
    fig.update_layout(**_base(420), coloraxis_showscale=False)
    fig.update_xaxes(title_text="Year", **GRID)
    fig.update_yaxes(title_text="Average VIX", **GRID)
    return fig
