import requests
import time
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine

# --- CẤU HÌNH POSTGRESQL ---
# Thay mat_khau_cua_ban bằng password của bạn
DB_URL = "postgresql://postgres:anhquan26@localhost:5432/fraud_db"
engine = create_engine(DB_URL)

API_URL = "http://127.0.0.1:8000/api/v1/transactions/stream"

def fetch_stream_data(batch_size=20):
    try:
        response = requests.get(API_URL, params={"batch_size": batch_size}, timeout=5)
        if response.status_code == 200:
            return response.json()
        return []
    except requests.exceptions.ConnectionError:
        print("Đang chờ API Server khởi động...")
        return []

def transform_and_enrich(raw_data):
    if not raw_data:
        return pd.DataFrame()
    df = pd.DataFrame(raw_data)
    df['ingested_at'] = datetime.now()
    df['balance_anomaly_flag'] = (df['oldbalanceOrg'] - df['amount'] != df['newbalanceOrig']).astype(int)
    df['type'] = df['type'].str.upper()
    return df

def load_to_database(df):
    if df.empty: return
    try:
        df.to_sql("raw_transactions", con=engine, if_exists="append", index=False)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Đã nạp {len(df)} giao dịch vào PostgreSQL (fraud_db).")
    except Exception as e:
        print(f"Lỗi nạp dữ liệu: {str(e)}")

def main():
    print("Khởi động hệ thống Ingestion Pipeline (PostgreSQL)...")
    while True:
        raw_data = fetch_stream_data(batch_size=1000)
        enriched_df = transform_and_enrich(raw_data)
        load_to_database(enriched_df)
        time.sleep(0.2)

if __name__ == "__main__":
    main()