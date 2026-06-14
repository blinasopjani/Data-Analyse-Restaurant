# Restaurant Sales Analysis

A full-stack data analysis project for a restaurant's sales data — from raw CSV to interactive dashboard.

## What this project answers

- Which menu items sell the most (by quantity and by revenue)?
- What hours and days are busiest?
- What are the monthly revenue trends?
- Which categories drive the most profit?
- Which servers perform best?
- Cash vs card split over time?

## Stack

| Tool | Purpose |
|------|---------|
| Python | Core analysis and automation |
| pandas / numpy | Data cleaning and aggregation |
| SQL (SQLite) | Querying structured data |
| Power BI | Executive dashboards |
| Streamlit | Interactive web dashboard |
| Excel | Quick pivot reports |

## Project structure

```
Data Analyse Restaurant/
├── data/
│   └── restaurant_sales.csv     # Raw sales data
├── scripts/
│   ├── clean.py                 # Data cleaning pipeline
│   ├── analyse.py               # Core analysis functions
│   └── export_to_excel.py       # Export summary to Excel
├── notebooks/
│   └── exploration.ipynb        # Exploratory data analysis
├── dashboard/
│   └── app.py                   # Streamlit dashboard
├── requirements.txt
└── README.md
```

## Dataset columns

| Column | Description |
|--------|-------------|
| order_id | Unique order identifier |
| date | Order date (YYYY-MM-DD) |
| time | Order time (HH:MM) |
| day_of_week | Day name |
| menu_item | Item ordered |
| category | Item category (Pizza, Burger, Salad…) |
| quantity | Number of units sold |
| unit_price | Price per unit (£) |
| total_price | quantity × unit_price (£) |
| payment_method | Card or Cash |
| server | Server name |
| table_number | Table number |

## Getting started

```bash
pip install -r requirements.txt
streamlit run dashboard/app.py
```
