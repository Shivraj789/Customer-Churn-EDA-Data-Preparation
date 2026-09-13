from flask import Flask, render_template, request, redirect, url_for, flash
from pathlib import Path
import pandas as pd
import numpy as np
import json

app = Flask(__name__)
app.secret_key = "week2-eda-secret-key"

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

DATA_URL = "https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/master/data/Telco-Customer-Churn.csv"


def load_dataset():
    uploaded = list(UPLOAD_DIR.glob("*.csv"))
    if uploaded:
        return pd.read_csv(uploaded[-1])
    return pd.read_csv(DATA_URL)


def prepare_data(df):
    df = df.copy()
    df.columns = df.columns.str.strip()

    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype(str).str.strip()

    if "TotalCharges" in df.columns:
        df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
        if "tenure" in df.columns and "MonthlyCharges" in df.columns:
            mask = df["tenure"].eq(0) & df["TotalCharges"].isna()
            df.loc[mask, "TotalCharges"] = df.loc[mask, "MonthlyCharges"]

    df = df.drop_duplicates()

    for col in df.select_dtypes(include=np.number).columns:
        df[col] = df[col].fillna(df[col].median())

    if "Churn" in df.columns:
        df["ChurnFlag"] = df["Churn"].map({"Yes": 1, "No": 0})

    return df


def chart_data(df):
    charts = {}

    if "Churn" in df.columns:
        charts["churn"] = {
            "labels": df["Churn"].value_counts().index.tolist(),
            "values": df["Churn"].value_counts().values.tolist()
        }

    if "Contract" in df.columns and "Churn" in df.columns:
        ct = pd.crosstab(df["Contract"], df["Churn"])
        charts["contract"] = {
            "labels": ct.index.tolist(),
            "yes": ct["Yes"].tolist() if "Yes" in ct else [0] * len(ct),
            "no": ct["No"].tolist() if "No" in ct else [0] * len(ct)
        }

    if "tenure" in df.columns:
        hist, bins = np.histogram(df["tenure"], bins=10)
        charts["tenure"] = {
            "labels": [f"{bins[i]:.0f}-{bins[i+1]:.0f}" for i in range(len(hist))],
            "values": hist.tolist()
        }

    if "MonthlyCharges" in df.columns:
        hist, bins = np.histogram(df["MonthlyCharges"], bins=10)
        charts["charges"] = {
            "labels": [f"{bins[i]:.0f}-{bins[i+1]:.0f}" for i in range(len(hist))],
            "values": hist.tolist()
        }

    if "tenure" in df.columns and "MonthlyCharges" in df.columns:
        sample = df[["tenure", "MonthlyCharges"]].dropna().head(500)
        charts["scatter"] = {
            "x": sample["tenure"].tolist(),
            "y": sample["MonthlyCharges"].tolist()
        }

    return charts


def outlier_count(df, column):
    if column not in df.columns or not pd.api.types.is_numeric_dtype(df[column]):
        return 0
    q1 = df[column].quantile(.25)
    q3 = df[column].quantile(.75)
    iqr = q3 - q1
    return int(((df[column] < q1 - 1.5 * iqr) | (df[column] > q3 + 1.5 * iqr)).sum())


@app.route("/")
def dashboard():
    raw = load_dataset()
    df = prepare_data(raw)

    churn_rate = float(df["ChurnFlag"].mean() * 100) if "ChurnFlag" in df else 0
    avg_monthly = float(df["MonthlyCharges"].mean()) if "MonthlyCharges" in df else 0
    avg_tenure = float(df["tenure"].mean()) if "tenure" in df else 0

    stats = {
        "rows": len(df),
        "columns": len(df.columns),
        "churn_rate": round(churn_rate, 1),
        "avg_monthly": round(avg_monthly, 2),
        "avg_tenure": round(avg_tenure, 1),
        "missing": int(df.isna().sum().sum()),
        "outliers": outlier_count(df, "MonthlyCharges") + outlier_count(df, "TotalCharges"),
    }

    charts = chart_data(df)

    insights = []
    if "Contract" in df.columns and "ChurnFlag" in df.columns:
        rates = df.groupby("Contract")["ChurnFlag"].mean().sort_values(ascending=False) * 100
        if len(rates):
            insights.append(f"{rates.index[0]} customers show the highest churn rate at {rates.iloc[0]:.1f}%.")
    if "tenure" in df.columns:
        insights.append("Short-tenure customers should be monitored closely because early customer experience can strongly affect retention.")
    if "MonthlyCharges" in df.columns:
        insights.append("Monthly charges are useful for segmentation and can help identify higher-value or higher-risk customer groups.")

    return render_template("dashboard.html", stats=stats, charts=charts, insights=insights)


@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("dataset")
    if not file or not file.filename.lower().endswith(".csv"):
        flash("Please select a CSV dataset.", "error")
        return redirect(url_for("dashboard"))

    for old in UPLOAD_DIR.glob("*.csv"):
        old.unlink()

    file.save(UPLOAD_DIR / "uploaded_dataset.csv")
    flash("Dataset uploaded successfully.", "success")
    return redirect(url_for("dashboard"))


@app.route("/reset")
def reset():
    for old in UPLOAD_DIR.glob("*.csv"):
        old.unlink()
    flash("Dashboard reset to the default dataset.", "success")
    return redirect(url_for("dashboard"))


@app.route("/data")
def data_preview():
    df = prepare_data(load_dataset())
    preview = df.head(20).to_dict(orient="records")
    columns = df.columns.tolist()
    return render_template("data.html", rows=preview, columns=columns, total=len(df))


if __name__ == "__main__":
    app.run(debug=True)
