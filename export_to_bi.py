import pandas as pd
from sqlalchemy import create_engine
import os

# Kết nối vào Database
DB_URL = "sqlite:///fraud_transactions.db"
engine = create_engine(DB_URL)

def export_data_for_dashboard():
    print("Đang xuất dữ liệu từ Database ra file CSV cho Dashboard...")
    
    # Lấy toàn bộ dữ liệu hoặc có thể viết SQL JOIN các bảng nếu phức tạp hơn
    query = "SELECT * FROM raw_transactions"
    df = pd.read_sql(query, engine)
    
    # Lưu ra file CSV
    output_file = "fraud_dashboard_data.csv"
    df.to_csv(output_file, index=False)
    
    print(f"✅ Hoàn tất! Đã xuất {len(df)} dòng dữ liệu ra tệp: {os.path.abspath(output_file)}")
    print("Bây giờ bạn có thể mở Power BI / Tableau và Import file CSV này vào.")

if __name__ == "__main__":
    export_data_for_dashboard()