# 📈 VIX Fear Index Dashboard

**EDA Project | DataHub Finance VIX | Dataset ID: 70177628**  
**Course:** Exploratory Data Analysis | **Instructor:** Ali Hassan Sherazi  
**Submission Date:** 05-June-2026

---

## 📌 Project Overview

This dashboard performs a complete Exploratory Data Analysis (EDA) on the CBOE VIX Volatility Index dataset (1990–2026). The VIX, also known as the "Fear Index," measures expected stock market volatility. High VIX = investors are scared; low VIX = market is calm.

---

## 📁 Project Structure

```
vix_project/
├── data/
│   └── vix-daily.csv          # Original dataset (DO NOT RENAME)
├── notebooks/
│   └── analysis.ipynb         # EDA Jupyter Notebook
├── app.py                     # Main dashboard application
├── charts.py                  # All chart/visualization functions
├── filters.py                 # All filter and data processing functions
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

---

## ⚙️ Installation & Setup

### Step 1 — Clone or unzip the project
```bash
unzip vix_project.zip
cd vix_project
```

### Step 2 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 3 — Run the dashboard
```bash
streamlit run app.py
```

The dashboard will open at `http://localhost:8501`

---

## 📊 Charts Included

| # | Chart Type | Description |
|---|-----------|-------------|
| 1 | Line + Area | VIX Trend Over Time with Crisis Annotations |
| 2 | Line (Multi) | 30-day & 252-day Moving Averages |
| 3 | Pie | Fear Zone Distribution (% of days) |
| 4 | Histogram | VIX Value Distribution by Fear Zone |
| 5 | Box Plot | VIX Spread by Decade (Seaborn) |
| 6 | Count Plot | Trading Days per Fear Zone (Seaborn) |
| 7 | Violin Plot | VIX Probability Density by Decade (Seaborn) |
| 8 | Bar | Yearly Average VIX |
| 9 | Scatter | VIX Open vs Close Relationship |
| 10 | Heatmap | Monthly Seasonality (Year × Month) |
| 11 | Bar (H) | Top 20 Highest VIX Days All Time |

---

## 🎛️ Dashboard Filters

All filters are connected to all charts and update dynamically:

- **Date Range** — Filter by Start and End date
- **VIX Range Slider** — Filter by minimum and maximum VIX value
- **Zone Multi-Select** — Select one or more Fear Zones
- **Date Search** — Type a specific date (YYYY-MM-DD) to find that day
- **Reset Button** — Resets all filters to default instantly

---

## 💡 Key Insights

1. **COVID-19 Peak (March 2020)** produced the highest ever VIX close of **82.69** — surpassing even the 2008 financial crisis.
2. **2008 Financial Crisis** dominates the Top 20 highest VIX days list, with 15 out of 20 entries.
3. **Most days (50%)** fall in the "Normal" zone (VIX 15–25), while only **3.8%** of days are "Extreme" (VIX > 35).
4. **October** is historically the most volatile month — multiple major crashes occurred in October.
5. **2017** recorded the calmest market — VIX hit its all-time low of **9.14** on November 3, 2017.
6. The **252-day moving average** shows a clear long-term upward bias in volatility post-2008.

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| Python 3.x | Core language |
| Pandas | Data loading, cleaning, filtering |
| NumPy | Numerical operations |
| Matplotlib | Static chart creation (mandatory) |
| Seaborn | Statistical visualizations (mandatory) |
| Plotly | Interactive charts |
| Streamlit | Dashboard framework |

---

## 🚀 Live Deployment

Dashboard deployed at: `https://vixedaproject70177628.streamlit.app`
