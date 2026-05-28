"""
filters.py
----------
All filter and data processing functions for VIX Dashboard.
"""

import pandas as pd
import streamlit as st


def load_and_prepare(filepath: str) -> pd.DataFrame:
    """Load CSV, parse dates, add derived columns."""
    df = pd.read_csv(filepath)
    df["DATE"]   = pd.to_datetime(df["DATE"])
    df["MA_30"]  = df["CLOSE"].rolling(30).mean()
    df["MA_252"] = df["CLOSE"].rolling(252).mean()
    df["Year"]   = df["DATE"].dt.year
    df["Month"]  = df["DATE"].dt.month
    df["Quarter"]= df["DATE"].dt.quarter
    df["Decade"] = (df["Year"] // 10 * 10).astype(str) + "s"
    df["Zone"]   = pd.cut(
        df["CLOSE"],
        bins=[0, 15, 25, 35, 9999],
        labels=["Low (<15)", "Normal (15-25)", "High (25-35)", "Extreme (>35)"]
    )
    return df


def render_sidebar_filters(df: pd.DataFrame):
    """
    Render all sidebar filters and return filtered dataframe + filter values.
    Sir required: Date range, Category, Numerical slider, Multi-select, Search, Reset.
    """
    with st.sidebar:
        st.markdown("## 🎛️ Dashboard Filters")
        st.markdown("---")

        # ── Reset Button ──────────────────────────────────────────────────────
        if st.button("🔄 Reset All Filters", use_container_width=True):
            st.session_state["start_date"] = df["DATE"].min().date()
            st.session_state["end_date"]   = df["DATE"].max().date()
            st.session_state["vix_range"]  = (float(df["CLOSE"].min()), float(df["CLOSE"].max()))
            st.session_state["zones"]      = ["Low (<15)", "Normal (15-25)", "High (25-35)", "Extreme (>35)"]
            st.session_state["search"]     = ""

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

        # ── 2. Numerical Range Slider ─────────────────────────────────────────
        st.markdown("**📊 VIX Close Range**")
        vix_min = float(df["CLOSE"].min())
        vix_max = float(df["CLOSE"].max())
        vix_range = st.slider("Select VIX Range", vix_min, vix_max,
                              (vix_min, vix_max), step=0.5, key="vix_range")
        st.markdown("---")

        # ── 3. Multi-Select Zone Filter ───────────────────────────────────────
        st.markdown("**🎯 Fear Zone Filter**")
        all_zones = ["Low (<15)", "Normal (15-25)", "High (25-35)", "Extreme (>35)"]
        zones = st.multiselect("Select Zones", all_zones, default=all_zones, key="zones")
        st.markdown("---")

        # ── 4. Search / Text Filter ───────────────────────────────────────────
        st.markdown("**🔍 Search by Date**")
        search = st.text_input("Type a date (e.g. 2008-10-24)", value="", key="search",
                               placeholder="YYYY-MM-DD")
        st.markdown("---")

        # ── About VIX ─────────────────────────────────────────────────────────
        st.markdown("**ℹ️ About VIX Zones**")
        st.markdown(
            "🟢 **< 15** — Market calm\n\n"
            "🔵 **15–25** — Normal\n\n"
            "🟠 **25–35** — High fear\n\n"
            "🔴 **> 35** — Extreme panic"
        )

    # ── Apply All Filters ─────────────────────────────────────────────────────
    if not zones:
        zones = all_zones  # default if nothing selected

    mask = (
        (df["DATE"] >= pd.to_datetime(start_date)) &
        (df["DATE"] <= pd.to_datetime(end_date))   &
        (df["CLOSE"] >= vix_range[0])              &
        (df["CLOSE"] <= vix_range[1])              &
        (df["Zone"].isin(zones))
    )

    dff = df.loc[mask].copy()

    # Apply search filter on top
    if search.strip():
        try:
            search_date = pd.to_datetime(search.strip())
            dff = dff[dff["DATE"].dt.date == search_date.date()]
        except Exception:
            pass  # invalid date input — ignore

    return dff, start_date, end_date
