import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# Load data
df = pd.read_csv('vix-daily.csv')
df['DATE'] = pd.to_datetime(df['DATE'])

# Add moving averages
df['MA_30'] = df['CLOSE'].rolling(window=30).mean()
df['MA_252'] = df['CLOSE'].rolling(window=252).mean()

st.title("📈 VIX Fear Index Dashboard")

# Chart 1: Time Series (✓ Already showing)
fig1 = px.line(df, x='DATE', y='CLOSE', title='VIX Trend Over Time')
st.plotly_chart(fig1, use_container_width=True)

# Chart 2: Moving Averages (Add this)
st.subheader("Moving Averages")
fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=df['DATE'], y=df['CLOSE'], name='VIX', line=dict(color='blue')))
fig2.add_trace(go.Scatter(x=df['DATE'], y=df['MA_30'], name='30-day MA', line=dict(color='orange')))
fig2.add_trace(go.Scatter(x=df['DATE'], y=df['MA_252'], name='252-day MA', line=dict(color='red')))
st.plotly_chart(fig2, use_container_width=True)

# Chart 3: Yearly Average (Add this)
st.subheader("Yearly Average VIX")
df['Year'] = df['DATE'].dt.year
yearly_avg = df.groupby('Year')['CLOSE'].mean().reset_index()
fig3 = px.bar(yearly_avg, x='Year', y='CLOSE', title='Average VIX by Year')
st.plotly_chart(fig3, use_container_width=True)

# Chart 4: Monthly Heatmap (Add this)
st.subheader("Monthly Seasonality Heatmap")
df['Month'] = df['DATE'].dt.month
df['Year'] = df['DATE'].dt.year
monthly_pivot = df.pivot_table(values='CLOSE', index='Year', columns='Month', aggfunc='mean')
fig4 = px.imshow(monthly_pivot, title='VIX Monthly Heatmap', color_continuous_scale='RdYlGn_r')
st.plotly_chart(fig4, use_container_width=True)

# Chart 5: Distribution with Zones (Enhance existing)
st.subheader("VIX Distribution by Zones")
def categorize_vix(value):
    if value < 15: return 'Low (<15)'
    elif value < 25: return 'Normal (15-25)'
    elif value < 35: return 'High (25-35)'
    else: return 'Extreme (>35)'

df['Zone'] = df['CLOSE'].apply(categorize_vix)
fig5 = px.histogram(df, x='CLOSE', color='Zone', nbins=50, 
                    title='VIX Distribution by Fear Zones',
                    color_discrete_map={'Low (<15)': 'green', 'Normal (15-25)': 'blue', 
                                       'High (25-35)': 'orange', 'Extreme (>35)': 'red'})
st.plotly_chart(fig5, use_container_width=True)

# Chart 6: Top 20 Highest VIX Days (Add this)
st.subheader("Top 20 Highest VIX Days")
top_20 = df.nlargest(20, 'CLOSE')
fig6 = px.bar(top_20, x='DATE', y='CLOSE', 
              title='Top 20 Highest VIX Close Values',
              hover_data=['DATE', 'CLOSE'])
st.plotly_chart(fig6, use_container_width=True)
