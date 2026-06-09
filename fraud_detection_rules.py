import pandas as pd
from sqlalchemy import create_engine

# --- CẤU HÌNH POSTGRESQL ---
DB_URL = "postgresql://postgres:anhquan26@localhost:5432/fraud_db"
engine = create_engine(DB_URL)

def run_advanced_fraud_rules():
    print("🚀 ĐANG QUÉT HỆ THỐNG VỚI CÁC RULE NÂNG CẤP...\n")
    
    # Kiểm tra số lượng Data
    try:
        total = pd.read_sql("SELECT COUNT(*) as cnt FROM raw_transactions", engine).iloc[0]['cnt']
        print(f"📊 Hệ thống đang phân tích {total} giao dịch...\n")
        if total < 100:
            print("⏳ Dữ liệu còn hơi ít để chạy thống kê, bạn cứ để luồng Ingestion chạy thêm nhé.\n")
    except Exception as e:
        print("Lỗi kết nối DB:", e)
        return

    # ==========================================
    # RULE 1: SYSTEM GLITCH / ACCOUNT MULE
    # Chuyển số tiền lớn (>100k) nhưng số dư trước/sau đều bằng 0
    # ==========================================
    query_rule_1 = """
    SELECT step, type, amount, "nameOrig", "oldbalanceOrg", "newbalanceOrig", ingested_at
    FROM raw_transactions
    WHERE type = 'TRANSFER' 
      AND amount > 100000 
      AND "oldbalanceOrg" = 0 
      AND "newbalanceOrig" = 0
    ORDER BY amount DESC
    LIMIT 5;
    """
    df_1 = pd.read_sql(query_rule_1, engine)
    print("🚨 RULE 1: LỢI DỤNG LỖ HỔNG (Chuyển tiền ảo / Số dư 0đ):")
    if not df_1.empty:
        print(df_1.to_string(index=False))
    else:
        print("✅ Chưa phát hiện.")
    print("-" * 75)

    # ==========================================
    # RULE 2: VELOCITY / SMURFING (RỬA TIỀN CHIA NHỎ)
    # Dùng CTEs đếm số lượng giao dịch của 1 tài khoản trong cùng 1 step (1 giờ)
    # ==========================================
    query_rule_2 = """
    WITH UserVelocity AS (
        SELECT 
            "nameOrig", 
            step,
            COUNT(*) as tx_count,
            SUM(amount) as total_volume,
            MAX(ingested_at) as last_tx_time
        FROM raw_transactions
        GROUP BY "nameOrig", step
    )
    SELECT "nameOrig", step, tx_count, total_volume, last_tx_time
    FROM UserVelocity 
    WHERE tx_count >= 3 
    ORDER BY tx_count DESC, total_volume DESC 
    LIMIT 5;
    """
    df_2 = pd.read_sql(query_rule_2, engine)
    print("🚨 RULE 2: VẬN TỐC GIAO DỊCH CAO (>= 3 giao dịch/giờ):")
    if not df_2.empty:
        print(df_2.to_string(index=False))
    else:
        print("✅ Chưa phát hiện (Cần chờ luồng API bơm thêm data trùng user).")
    print("-" * 75)

    # ==========================================
    # RULE 3: ĐỘT BIẾN THỐNG KÊ (3-SIGMA ANOMALY)
    # Tìm các giao dịch vượt quá: Trung bình + 3*Độ_lệch_chuẩn
    # ==========================================
    query_rule_3 = """
    WITH GlobalStats AS (
        SELECT 
            type, 
            AVG(amount) as mu_amount, 
            COALESCE(STDDEV(amount), 0) as sigma_amount
        FROM raw_transactions
        GROUP BY type
    )
    SELECT 
        r.step, 
        r.type, 
        r.amount, 
        ROUND(s.mu_amount::numeric, 2) as avg_for_this_type, 
        r."nameOrig"
    FROM raw_transactions r
    JOIN GlobalStats s ON r.type = s.type
    WHERE s.sigma_amount > 0 
      AND r.amount > (s.mu_amount + 3 * s.sigma_amount)
    ORDER BY r.amount DESC 
    LIMIT 5;
    """
    df_3 = pd.read_sql(query_rule_3, engine)
    print("🚨 RULE 3: ĐỘT BIẾN THỐNG KÊ (Vượt ngưỡng 3-Sigma):")
    if not df_3.empty:
        print(df_3.to_string(index=False))
    else:
        print("✅ Chưa phát hiện đột biến.")
    print("-" * 75)

if __name__ == "__main__":
    run_advanced_fraud_rules()