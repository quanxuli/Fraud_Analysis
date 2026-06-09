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