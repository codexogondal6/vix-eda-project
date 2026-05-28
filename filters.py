"""
filters.py
----------
All filter and data processing functions for VIX Dashboard.
Sir required: Date range, Category Dropdown, Numerical slider,
              Multi-select, Search/Text, Reset button.
"""

import pandas as pd
import streamlit as st


def load_and_prepare(filepath: str) -> pd.DataFrame:
    """Load CSV, parse dates, add derived columns."""
    df = pd.read_csv(filepath)
    df["DATE"]    = pd.to_datetime(df["DATE"])
    df["MA_30"]   = df["CLOSE"].rolling(30).mean()
    df["MA_252"]  = df["CLOSE"].rolling(252).mean()
    df["Year"]    = df["DATE"].dt.year
    df["Month"]   = df["DATE"].dt.month
    df["Quarter"] = df["DATE"].dt.quarter
    df["Decade"]  = (df["Year"] // 10 * 10).astype(str) + "s"
    df["Zone"]    = pd.cut(
        df["CLOSE"],
        bins=[0, 15, 25, 35, 9999],
        labels=["Low (<15)", "Normal (15-25)", "High (25-35)", "Extreme (>35)"]
    )
    return df


def render_sidebar_filters(df: pd.DataFrame):
    """
    Render all sidebar filters and return filtered dataframe + filter values.
    """
    all_zones  = ["Low (<15)", "Normal (15-25)", "High (25-35)", "Extreme (>35)"]
    all_years  = sorted(df["Year"].unique().tolist())
    month_map  = {0:"All Months",1:"January",2:"February",3:"March",
                  4:"April",5:"May",6:"June",7:"July",8:"August",
                  9:"September",10:"October",11:"November",12:"December"}

    with st.sidebar:
        st.markdown("## 🎛️ Dashboard Filters")
        st.markdown("---")

        # ── Reset Button ──────────────────────────────────────────────────────
        if st.button("🔄 Reset All Filters", use_container_width=True):
            st.session_state["start_date"]  = df["DATE"].min().date()
            st.session_state["end_date"]    = df["DATE"].max().date()
            st.session_state["vix_range"]   = (float(df["CLOSE"].min()),
                                               float(df["CLOSE"].max()))
            st.session_state["zones"]       = all_zones
            st.session_state["year_select"] = 0          # 0 = All Years
            st.session_state["month_select"]= 0          # 0 = All Months
            st.session_state["search"]      = ""
            st.rerun()

        st.markdown("---")

        # ── 1. Date Range Filter ──────────────────────────────────────────────
        st.markdown("**📅 Date Range**")
        min_d = df["DATE"].min().date()
        max_d = df["DATE"].max().date()
        start_date = st.date_input("Start Date", min_d,
                                   min_value=min_d, max_value=max_d,
                                   key="start_date")
        end_date   = st.date_input("End Date", max_d,
                                   min_value=min_d, max_value=max_d,
                                   key="end_date")
        st.markdown("---")

        # ── 2. Category Dropdown — Year ───────────────────────────────────────
        st.markdown("**📆 Filter by Year**")
        year_options = [0] + all_years          # 0 = All Years
        year_labels  = ["All Years"] + [str(y) for y in all_years]
        selected_year_idx = st.selectbox(
            "Select Year",
            options=range(len(year_options)),
            format_func=lambda i: year_labels[i],
            index=0,
            key="year_select"
        )
        selected_year = year_options[selected_year_idx]

        # ── 3. Category Dropdown — Month ──────────────────────────────────────
        st.markdown("**🗓️ Filter by Month**")
        month_options = list(range(13))         # 0 = All Months
        selected_month = st.selectbox(
            "Select Month",
            options=month_options,
            format_func=lambda m: month_map[m],
            index=0,
            key="month_select"
        )
        st.markdown("---")

        # ── 4. Numerical Range Slider ─────────────────────────────────────────
        st.markdown("**📊 VIX Close Range**")
        vix_min = float(df["CLOSE"].min())
        vix_max = float(df["CLOSE"].max())
        vix_range = st.slider("Select VIX Range", vix_min, vix_max,
                              (vix_min, vix_max), step=0.5, key="vix_range")
        st.markdown("---")

        # ── 5. Multi-Select Zone Filter ───────────────────────────────────────
        st.markdown("**🎯 Fear Zone (Multi-Select)**")
        zones = st.multiselect("Select Zones", all_zones,
                               default=all_zones, key="zones")
        st.markdown("---")

        # ── 6. Search / Text Filter ───────────────────────────────────────────
        st.markdown("**🔍 Search by Date**")
        search = st.text_input("Type a date (e.g. 2008-10-24)",
                               value="", key="search",
                               placeholder="YYYY-MM-DD")
        st.markdown("---")

        # ── About VIX ─────────────────────────────────────────────────────────
        st.markdown("**ℹ️ VIX Fear Zones**")
        st.markdown(
            "🟢 **< 15** — Market calm\n\n"
            "🔵 **15–25** — Normal\n\n"
            "🟠 **25–35** — High fear\n\n"
            "🔴 **> 35** — Extreme panic"
        )

    # ── Apply All Filters ─────────────────────────────────────────────────────
    if not zones:
        zones = all_zones

    mask = (
        (df["DATE"] >= pd.to_datetime(start_date)) &
        (df["DATE"] <= pd.to_datetime(end_date))   &
        (df["CLOSE"] >= vix_range[0])              &
        (df["CLOSE"] <= vix_range[1])              &
        (df["Zone"].isin(zones))
    )

    # Category dropdown filters
    if selected_year != 0:
        mask = mask & (df["Year"] == selected_year)
    if selected_month != 0:
        mask = mask & (df["Month"] == selected_month)

    dff = df.loc[mask].copy()

    # Search filter
    if search.strip():
        try:
            search_date = pd.to_datetime(search.strip())
            dff = dff[dff["DATE"].dt.date == search_date.date()]
        except Exception:
            pass

    return dff, start_date, end_date
