from flask import Flask, render_template, request, redirect, url_for, flash
from pathlib import Path
import pandas as pd
import numpy as np

app = Flask(__name__)
app.secret_key = "churnlab-week2"

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
    df.columns = df.columns.astype(str).str.strip()

    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype(str).str.strip()

    if "TotalCharges" in df.columns:
        df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
        if "tenure" in df.columns and "MonthlyCharges" in df.columns:
            mask = df["tenure"].eq(0) & df["TotalCharges"].isna()
            df.loc[mask, "TotalCharges"] = df.loc[mask, "MonthlyCharges"]

    before = len(df)
    df = df.drop_duplicates()
    duplicates_removed = before - len(df)

    for col in df.select_dtypes(include=np.number).columns:
        df[col] = df[col].fillna(df[col].median())

    if "Churn" in df.columns:
        df["ChurnFlag"] = df["Churn"].map({"Yes": 1, "No": 0}).fillna(0)

    return df, duplicates_removed


def distribution(df, column):
    if column not in df.columns:
        return []
    counts = df[column].value_counts(dropna=False)
    total = max(len(df), 1)
    return [
        {"label": str(label), "count": int(count), "percent": round(count / total * 100, 1)}
        for label, count in counts.head(10).items()
    ]


def histogram(df, column, bins=10):
    if column not in df.columns or not pd.api.types.is_numeric_dtype(df[column]):
        return []
    values = df[column].dropna()
    if values.empty or values.min() == values.max():
        return []
    counts, edges = np.histogram(values, bins=bins)
    maximum = max(int(counts.max()), 1)
    return [
        {"label": f"{edges[i]:.0f}–{edges[i + 1]:.0f}", "count": int(counts[i]), "percent": round(counts[i] / maximum * 100, 1)}
        for i in range(len(counts))
    ]


def outlier_count(df, column):
    if column not in df.columns or not pd.api.types.is_numeric_dtype(df[column]):
        return 0
    q1 = df[column].quantile(0.25)
    q3 = df[column].quantile(0.75)
    iqr = q3 - q1
    return int(((df[column] < q1 - 1.5 * iqr) | (df[column] > q3 + 1.5 * iqr)).sum())


@app.route("/")
def dashboard():
    raw = load_dataset()
    df, duplicates_removed = prepare_data(raw)

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
        "duplicates": duplicates_removed,
        "outliers": outlier_count(df, "MonthlyCharges") + outlier_count(df, "TotalCharges"),
    }

    contract_distribution = []
    if "Contract" in df.columns and "Churn" in df.columns:
        table = pd.crosstab(df["Contract"], df["Churn"])
        for contract, row in table.iterrows():
            total = int(row.sum())
            churned = int(row.get("Yes", 0))
            rate = round(churned / total * 100, 1) if total else 0
            contract_distribution.append({"label": str(contract), "count": total, "churn": churned, "rate": rate})
        contract_distribution.sort(key=lambda x: x["rate"], reverse=True)

    insights = []
    if contract_distribution:
        top = contract_distribution[0]
        insights.append(f"{top['label']} customers have the highest churn rate at {top['rate']}%.")
    insights.append("Short-tenure customers are an important retention group to monitor.")
    insights.append("Monthly charges can help segment customers by billing level and churn risk.")

    return render_template(
        "dashboard.html",
        stats=stats,
        churn_distribution=distribution(df, "Churn"),
        contract_distribution=contract_distribution,
        tenure_distribution=histogram(df, "tenure"),
        charges_distribution=histogram(df, "MonthlyCharges"),
        insights=insights,
    )


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
    df, _ = prepare_data(load_dataset())
    return render_template("data.html", rows=df.head(20).fillna("").to_dict(orient="records"), columns=df.columns.tolist(), total=len(df))


@app.route("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
