
import streamlit as st
import pandas as pd
import plotly.express as px

# Page Config
st.set_page_config(page_title="VIX Dashboard", layout="wide")

# Title
st.title("📈 VIX Fear Index Dashboard")
st.markdown("Interactive visualization of Volatility Index (1990-2026)")

# Load Data
@st.cache_data
def load_data():
    # Yeh try/except block error handle karega agar file na mile
    try:
        df = pd.read_csv('vix-daily-cleaned.csv')
        df['DATE'] = pd.to_datetime(df['DATE'])
        return df
    except FileNotFoundError:
        st.error("File not found! Please upload vix-daily-cleaned.csv to the folder.")
        return None

df = load_data()

if df is not None:
    # Sidebar Filter
    start_date = st.sidebar.date_input("Start Date", df['DATE'].min())
    end_date = st.sidebar.date_input("End Date", df['DATE'].max())
    
    # Filter Data
    mask = (df['DATE'] >= pd.to_datetime(start_date)) & (df['DATE'] <= pd.to_datetime(end_date))
    df_filtered = df.loc[mask]

    # Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Current VIX", f"{df_filtered['CLOSE'].iloc[-1]:.2f}")
    col2.metric("Average VIX", f"{df_filtered['CLOSE'].mean():.2f}")
    col3.metric("Max VIX (All Time)", f"{df['CLOSE'].max():.2f}")

    # Chart 1: Line Chart
    st.subheader("VIX Trend Over Time")
    fig = px.line(df_filtered, x='DATE', y='CLOSE', height=400)
    st.plotly_chart(fig, use_container_width=True)

    # Chart 2: Distribution
    st.subheader("VIX Distribution")
    fig2 = px.histogram(df_filtered, x='CLOSE', nbins=50, height=300)
    st.plotly_chart(fig2, use_container_width=True)
