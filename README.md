# ChurnLab — Flask EDA Dashboard

A polished Flask web application for the YUVA Intern Week 2 assignment: **Exploratory Data Analysis and Data Preparation**.

## Features

- Interactive analytics dashboard
- Customer churn KPI cards
- Churn distribution chart
- Contract vs churn comparison
- Tenure and monthly-charge distributions
- Customer-level scatter analysis
- Automatic data cleaning
- Missing-value handling
- Duplicate removal
- Numeric type conversion
- IQR outlier inspection
- CSV upload support
- Cleaned data preview
- Responsive UI

## Tech Stack

- Python
- Flask
- Pandas
- NumPy
- HTML/CSS
- JavaScript
- Chart.js

## Run on Mac

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 app.py
```

Open:

```text
http://127.0.0.1:5000
```

## Project Structure

```text
customer-churn-flask-dashboard/
├── app.py
├── requirements.txt
├── README.md
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   └── data.html
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── dashboard.js
└── uploads/
```

## Dataset

The default dashboard uses the IBM Telco Customer Churn public dataset. You can also upload another CSV from the dashboard.

## Assignment Mapping

| YUVA Requirement | Implementation |
|---|---|
| Public dataset | Telco Customer Churn |
| Data cleaning | Pandas cleaning pipeline |
| Missing values | Numeric median + zero-tenure handling |
| Duplicate detection | `drop_duplicates()` |
| Outlier detection | IQR method |
| Summary statistics | Dashboard metrics |
| Histograms | Tenure + Monthly Charges |
| Scatter plot | Tenure vs Monthly Charges |
| Pattern analysis | Churn and contract charts |
| Documentation | README + report |
# Customer-Churn-EDA-Data-Preparation
