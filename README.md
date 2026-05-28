# VIX Volatility Index - Exploratory Data Analysis & Interactive Dashboard

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-FF4B4B.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 📊 Project Overview

This project performs comprehensive **Exploratory Data Analysis (EDA)** on the **CBOE Volatility Index (VIX)**, also known as the "Fear Index," spanning over **36 years of market data** (1990-2026). The project includes data cleaning, statistical analysis, interactive visualizations, and a deployed Streamlit web application for real-time data exploration.

## 🎯 Objectives

- Analyze historical VIX trends and market volatility patterns
- Identify crisis periods and market fear peaks
- Create interactive visualizations for better insights
- Build a deployable web dashboard for public access
- Understand market sentiment through volatility analysis

## 📁 Dataset

**File:** `vix-daily.csv`

| Attribute | Details |
|-----------|---------|
| **Total Records** | 9,190 rows |
| **Date Range** | January 1990 - May 2026 |
| **Columns** | DATE, OPEN, HIGH, LOW, CLOSE |
| **Max VIX** | 82.69 (March 2020 - COVID-19 Crisis) |
| **Min VIX** | 9.14 |
| **Average VIX** | ~19.45 |

## ✨ Features

### 🔍 Data Analysis
- **Data Cleaning & Preprocessing**: Datetime conversion, missing value handling
- **Feature Engineering**: Year, Month, Quarter extraction, Moving averages (30-day & 252-day)
- **Statistical Analysis**: Mean, median, standard deviation, skewness
- **VIX Zone Classification**:
  - Low Volatility: < 15
  - Normal: 15-25
  - High: 25-35
  - Extreme: > 35

### 📈 Visualizations
1. **Time Series Analysis**: Complete historical VIX trend with crisis annotations
2. **Moving Averages**: 30-day vs 252-day trend comparison
3. **Yearly Trends**: Average VIX by year bar chart
4. **Monthly Seasonality**: Heatmap showing volatility patterns
5. **Distribution Analysis**: Histogram with zone-based coloring
6. **Top 20 Fear Days**: Highest VIX spikes visualization

### 🌐 Interactive Web App
- Date range filtering
- Interactive Plotly charts
- Real-time statistics cards
- Responsive design
- Public deployment on Render

## 🛠️ Technologies Used

| Technology | Purpose |
|------------|---------|
| **Python 3.8+** | Core programming language |
| **Pandas** | Data manipulation and analysis |
| **NumPy** | Numerical computations |
| **Matplotlib** | Static visualizations |
| **Seaborn** | Statistical graphics |
| **Plotly** | Interactive visualizations |
| **Streamlit** | Web application framework |
| **Render** | Cloud deployment platform |

## 📥 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Git

### Local Development

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/vix-eda-project.git
cd vix-eda-project
```

2. **Create a virtual environment (recommended):**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Run the Streamlit app:**
```bash
streamlit run app.py
```

5. **Open your browser:**
Navigate to `http://localhost:8501`

📁 Project Structure
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

## 🚀 Deployment

The application is deployed on **Render** for public access.

### Deployment Steps:

1. **Push code to GitHub**
2. **Create Render account** at [render.com](https://render.com)
3. **Create new Web Service**
4. **Connect GitHub repository**
5. **Configure settings:**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `streamlit run app.py`
6. **Deploy** and get your live URL

**Live Demo:** [https://your-vix-app.onrender.com](https://your-vix-app.onrender.com)

## 📊 Key Insights

### Historical Analysis
- **Highest Volatility**: March 2020 (COVID-19 pandemic) - VIX reached 82.69
- **2008 Financial Crisis**: VIX peaked around 80+
- **2022 Ukraine War**: Significant volatility spike
- **Lowest Periods**: Generally during stable economic periods (mid-1990s, 2017)

### Seasonal Patterns
- **High Volatility Months**: September, October, March
- **Low Volatility Months**: December, January, summer months

### Statistical Summary
- **Mean VIX**: ~19.45
- **Standard Deviation**: ~8.5
- **Skewness**: Positive (right-skewed distribution)
- **Most Common Range**: 15-25 (Normal volatility)

## 📈 Usage Examples

### Basic Analysis
```python
import pandas as pd
import plotly.express as px

# Load data
df = pd.read_csv('data/vix-daily.csv')
df['DATE'] = pd.to_datetime(df['DATE'])

# Calculate moving average
df['MA_30'] = df['CLOSE'].rolling(window=30).mean()

# Create visualization
fig = px.line(df, x='DATE', y=['CLOSE', 'MA_30'], 
              title='VIX with 30-Day Moving Average')
fig.show()
```

### VIX Zone Classification
```python
def classify_vix(value):
    if value < 15:
        return "Low"
    elif value < 25:
        return "Normal"
    elif value < 35:
        return "High"
    else:
        return "Extreme"

df['Volatility_Zone'] = df['CLOSE'].apply(classify_vix)
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Your Name**
- GitHub: https://github.com/codexogondal6
- Email:  70177628@student.uol.edu.pk
- LinkedIn:https://linkedin.com/in/gondalfounder

## 🙏 Acknowledgments

- **CBOE** (Chicago Board Options Exchange) for VIX data
- **Kaggle** for dataset availability
- **Streamlit** team for the amazing web framework
- **Plotly** for interactive visualization library


## 🔗 References

- [VIX White Paper - CBOE](https://www.cboe.com/micro/vix/vixwhite.pdf)
- [Understanding VIX](https://www.investopedia.com/articles/trading/09/volatility-index-vix.asp)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Plotly Python Library](https://plotly.com/python/)

---

**⭐ If you found this project helpful, please give it a star on GitHub!**

**Last Updated:** May 2026
