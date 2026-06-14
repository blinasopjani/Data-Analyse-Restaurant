# 🍽️ RestaurantIQ: Restaurant Sales Analytics Dashboard

An interactive, premium sales analysis dashboard built with Python, Pandas, Plotly, and Streamlit. It transforms raw restaurant sales transaction logs into actionable business insights.

🌐 **Live Streamlit App:** [View Live Dashboard](https://data-analyse-restaurant-ubnunanagz3fgw2uv2znat.streamlit.app/)

---

## ✨ Features & Business Insights

- **📊 Sales Overview**: Track total revenue, order count, average transaction value, top menu items, and top servers at a glance.
- **🍕 Category & Menu Performance**: Identify which dishes generate the most revenue and volume to optimize menu pricing and item placement.
- **🕐 Time & Days Analysis**: Pinpoint exactly when the restaurant is busiest (hour of day, day of week) to improve staff scheduling.
- **👤 Staff Performance**: Monitor individual server statistics (orders served, revenue generated) to reward high performers.
- **💳 Payment Methods & Raw Data**: View cash vs. card preference distribution and explore full transaction details.

---

## 🛠️ Technology Stack

- **Frontend / UI**: [Streamlit](https://streamlit.io/) (configured with a responsive, modern dark-navy sidebar and coral theme)
- **Data Engineering**: [Pandas](https://pandas.pydata.org/) & [NumPy](https://numpy.org/) for robust data cleaning, validation, and analytics aggregation
- **Visualization**: [Plotly Express](https://plotly.com/python/) for interactive charts and graphs
- **Font & Styling**: Custom integration with Google Font `Outfit` and custom inline CSS enhancements

---

## 📂 Project Structure

```text
Data-Analyse-Restaurant/
├── .streamlit/
│   └── config.toml          # Custom Streamlit theme color config
├── dashboard/
│   └── app.py               # Streamlit application entrypoint & dashboard code
├── data/
│   └── restaurant_sales.csv # Raw sales transactions dataset (CSV)
├── scripts/
│   ├── clean.py             # Data loading and pipeline cleaning script
│   ├── analyse.py           # Core analytics aggregation functions
│   └── export_to_excel.py   # Utility to export aggregations to Excel
├── .gitignore
├── requirements.txt         # Dependencies
└── README.md                # Project documentation
```

---

## ⚙️ Running Locally

1. **Clone the repository:**
   ```bash
   git clone https://github.com/blinasopjani/Data-Analyse-Restaurant.git
   cd Data-Analyse-Restaurant
   ```

2. **Install requirements:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Launch the dashboard:**
   ```bash
   streamlit run dashboard/app.py
   ```
