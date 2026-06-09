# 🚨 FraudGuard: Enterprise Data Pipeline & ML for Financial Fraud Detection

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14.0+-336791.svg)
![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-Machine%20Learning-F7931E.svg)
![PowerBI](https://img.shields.io/badge/Power_BI-Dashboard-F2C811.svg)

## 📌 Executive Summary
This project simulates an enterprise-grade Data Engineering and Machine Learning pipeline designed for the financial sector. It ingests simulated high-frequency core banking transactions, processes them in real-time, stores them in a robust PostgreSQL data warehouse, and applies both **Advanced SQL Business Rules** and **Unsupervised Machine Learning** to detect fraudulent activities and optimize operational costs.

## 🏗️ Data Architecture & Pipeline

The system is built on a modern, decoupled architecture:

```text
[Mock Core Banking API] --(Streaming)--> [ETL Ingestion Pipeline]
    (FastAPI / Pandas)                           (Python / Pandas)
                                                        |
                                                        v
[Power BI Dashboard] <----(DirectQuery)---- [PostgreSQL Data Warehouse]
    (Real-time BI)                                      |
                                                        v
                                          [Machine Learning Pipeline]
                                        (Scikit-Learn Isolation Forest)
```
# 🚨 FraudGuard: Enterprise Data Pipeline & ML for Financial Fraud Detection

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14.0+-336791.svg)
![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-Machine%20Learning-F7931E.svg)
![PowerBI](https://img.shields.io/badge/Power_BI-Dashboard-F2C811.svg)

## 📌 Executive Summary
This project simulates an enterprise-grade Data Engineering and Machine Learning pipeline designed for the financial sector. It ingests simulated high-frequency core banking transactions, processes them in real-time, stores them in a robust PostgreSQL data warehouse, and applies both **Advanced SQL Business Rules** and **Unsupervised Machine Learning** to detect fraudulent activities and optimize operational costs.

## 🏗️ Data Architecture & Pipeline

The system is built on a modern, decoupled architecture:

```text
[Mock Core Banking API] --(Streaming)--> [ETL Ingestion Pipeline]
    (FastAPI / Pandas)                           (Python / Pandas)
                                                        |
                                                        v
[Power BI Dashboard] <----(DirectQuery)---- [PostgreSQL Data Warehouse]
    (Real-time BI)                                      |
                                                        v
                                          [Machine Learning Pipeline]
                                        (Scikit-Learn Isolation Forest)
```

## 🚀 Core Features & Business Value

### 1. Real-Time Data Ingestion (ETL)
* Built a custom **FastAPI** server to mock a core banking streaming endpoint.
* Developed an infinite-loop ingestion script to fetch, clean, and enrich data (calculating balance anomalies on the fly) before bulk-inserting into **PostgreSQL** via SQLAlchemy.

### 2. Advanced Rule-Based Detection (SQL)
Implemented complex business rules using SQL `Window Functions` and `CTEs`:
* **Velocity/Smurfing Rule:** Flags accounts executing >= 3 transfers within a 1-hour window.
* **Account Draining / System Glitch:** Detects massive wire transfers (> $100k) where the originating and destination balances incorrectly remain at zero.
* **3-Sigma Statistical Anomaly:** Flags transactions exceeding `μ + 3σ` of the global average.

### 3. Business Cost & Threshold Optimization
* Authored a script to evaluate the **Trade-off between False Positives (Customer Friction) and False Negatives (Fraud Loss)**.
* The system iteratively tests multiple threshold parameters to dynamically recommend the exact alerting threshold that minimizes total operational loss for the bank.

### 4. Machine Learning Anomaly Detection
* Deployed an Unsupervised Learning model (**Isolation Forest**) to detect hidden fraud patterns without relying on hard-coded SQL rules.
* Engineered features (One-Hot Encoding, StandardScaler) and scored millions of transactions, outputting a normalized `Risk Score (0-100)` back to the database for BI consumption.

## 📂 Repository Structure

```bash
├── data/
│   └── transactions.csv              # Raw Kaggle PaySim Dataset (Not uploaded due to size)
├── api_server.py                     # Mock Core Banking Streaming API (FastAPI)
├── data_ingestion.py                 # Continuous ETL Pipeline 
├── fraud_detection_rules.py          # SQL-based Fraud Rules Engine
├── threshold_optimization.py         # Cost Optimization Simulator
├── fraud_ml_pipeline.py              # Isolation Forest Scoring Job
└── README.md
```

## ⚙️ How to Run Locally

**1. Database Setup:**
Ensure PostgreSQL is running locally and create a blank database named `fraud_db`. Update the `DB_URL` credentials in the Python scripts.

**2. Install Dependencies:**
```bash
pip install fastapi uvicorn pandas scikit-learn sqlalchemy psycopg2-binary tqdm requests
```

**3. Launch the Pipeline (Run in 3 separate terminals):**

* **Terminal 1 (Start the Bank API):**
  ```bash
  uvicorn api_server:app --reload
  ```
* **Terminal 2 (Start Data Ingestion):**
  ```bash
  python data_ingestion.py
  ```
* **Terminal 3 (Run ML Scoring & Analytics):**
  ```bash
  # Wait for a few thousand rows to be ingested, then run:
  python fraud_ml_pipeline.py
  ```

## 📊 Business Intelligence (Power BI)
To visualize the data, connect Power BI to the local PostgreSQL database using **DirectQuery** mode. Connect to the `ml_scored_transactions` table to build risk distribution histograms and real-time fraud watchlists.

---
*Disclaimer: This project uses the synthetic [PaySim dataset](https://www.kaggle.com/datasets/ealaxi/paysim1) from Kaggle for educational and portfolio demonstration purposes.*