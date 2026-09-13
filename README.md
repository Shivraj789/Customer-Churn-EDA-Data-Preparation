# Customer Churn EDA & Data Preparation — Flask

A server-rendered **Flask + Pandas** dashboard for customer churn exploratory data analysis and data preparation.

## Features

- Customer churn KPIs
- Churn distribution
- Contract-wise churn analysis
- Tenure and monthly-charge distributions
- Automatic data cleaning
- Missing-value handling
- Duplicate removal
- Numeric conversion
- IQR outlier inspection
- CSV upload
- Cleaned data preview
- Responsive HTML/CSS UI
- **No JavaScript**
- Vercel-ready deployment

## Tech Stack

- Python
- Flask
- Pandas
- NumPy
- Jinja2
- HTML5
- CSS3
- Vercel

## Project Structure

```text
Customer-Churn-EDA-Data-Preparation/
├── app.py
├── api/
│   └── index.py
├── vercel.json
├── requirements.txt
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   └── data.html
├── static/
│   └── css/
│       └── style.css
└── uploads/
```

## Run locally on Mac

```bash
cd Customer-Churn-EDA-Data-Preparation
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 app.py
```

Open `http://127.0.0.1:5000`.

## Deploy to Vercel

This repository contains `vercel.json` and `api/index.py` for a Flask deployment. Import the GitHub repository into Vercel and deploy it as a Python project.

CLI option:

```bash
npm install -g vercel
vercel login
vercel
vercel --prod
```

## Important

The app does not use browser-side JavaScript or Chart.js. All analysis and visual bars are generated on the Flask server using Pandas/NumPy and rendered with Jinja templates.

## Interview explanation

> I built a server-rendered customer churn analytics application using Flask and Pandas. The backend performs data cleaning, missing-value handling, duplicate removal, numeric conversion, outlier inspection, churn-rate calculation, and statistical analysis. I kept the frontend JavaScript-free and used Jinja templates with HTML/CSS for rendering. The application is packaged for deployment on Vercel through a Python Flask entry point.
