import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

# --- 1. KẾT NỐI POSTGRESQL ---
DB_URL = "postgresql://postgres:anhquan26@localhost:5432/fraud_db"
engine = create_engine(DB_URL)

def run_ml_pipeline():
    print("🤖 KHỞI ĐỘNG MACHINE LEARNING PIPELINE...")
    
    # Kéo toàn bộ dữ liệu hiện có từ Postgres về DataFrame
    try:
        df = pd.read_sql("SELECT * FROM raw_transactions", engine)
        if len(df) < 500:
            print("⚠️ Cảnh báo: Dữ liệu hiện tại quá ít để train mô hình ML hiệu quả. Hãy để file Ingestion bơm thêm data!")
            return
        print(f"📊 Đã tải {len(df)} giao dịch từ Database để xử lý...")
    except Exception as e:
        print("🔴 Lỗi kết nối Database:", e)
        return

    # --- 2. FEATURE ENGINEERING (BIẾN ĐỔI ĐẶC TRƯNG) ---
    print("⚙️ Đang thực hiện Feature Engineering...")
    
    # Chuyển đổi biến phân loại (Categorical) là 'type' thành các cột số (One-Hot Encoding)
    df_encoded = pd.get_dummies(df, columns=['type'], drop_first=True)
    
    # Xác định danh sách các đặc trưng (Features) dùng để huấn luyện mô hình
    # Lấy các cột dummy của 'type' vừa tạo tự động
    type_cols = [col for col in df_encoded.columns if 'type_' in col]
    base_features = ['amount', 'oldbalanceOrg', 'newbalanceOrig', 'balance_anomaly_flag']
    feature_columns = base_features + type_cols
    
    # Tập dữ liệu đầu vào cho mô hình
    X = df_encoded[feature_columns]
    
    # Chuẩn hóa dữ liệu (Feature Scaling) để các cột có đơn vị lớn không áp đảo các cột nhỏ
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # --- 3. HUẤN LUYỆN MÔ HÌNH ISOLATION FOREST ---
    print("🧠 Đang huấn luyện mô hình Isolation Forest...")
    
    # contamination=0.01 nghĩa là ta giả định có khoảng 1% dữ liệu trong DB là bất thường/gian lận
    model = IsolationForest(contamination=0.01, random_state=42, n_estimators=100)
    model.fit(X_scaled)

    # --- 4. CHẤM ĐIỂM VÀ DỰ ĐOÁN (SCORING) ---
    print("🎯 Đang chấm điểm rủi ro cho từng giao dịch...")
    
    # Predict trả về: 1 (Hợp lệ), -1 (Bất thường)
    raw_predictions = model.predict(X_scaled)
    # Chuyển đổi định dạng: -1 thành 1 (Gian lận), 1 thành 0 (Hợp lệ) để đồng bộ làm Dashboard
    df['ml_fraud_flag'] = np.where(raw_predictions == -1, 1, 0)
    
    # Tính toán khoảng cách rủi ro (Anomalies Score). Điểm càng âm thì càng bất thường
    decision_scores = model.decision_function(X_scaled)
    
    # Chuẩn hóa điểm số này về thang điểm từ 0 đến 100 (Risk Score) cho dễ đọc trên BI Dashboard
    # Điểm tiến về 100 có độ rủi ro cực cao, tiến về 0 là an toàn
    min_s, max_s = decision_scores.min(), decision_scores.max()
    df['ml_risk_score'] = 100 * (max_s - decision_scores) / (max_s - min_s)
    df['ml_risk_score'] = df['ml_risk_score'].round(2)

    # --- 5. GHI KẾT QUẢ NGƯỢC LẠI POSTGRESQL ---
    # Chọn ra các cột cần thiết để xuất ra bảng phân tích cuối cùng
    output_cols = ['step', 'type', 'amount', 'nameOrig', 'oldbalanceOrg', 'newbalanceOrig', 
                   'nameDest', 'balance_anomaly_flag', 'ingested_at', 'ml_fraud_flag', 'ml_risk_score']
    df_output = df[output_cols]
    
    try:
        # Lưu vào bảng mới mang tên 'ml_scored_transactions'
        # if_exists='replace' để mỗi lần script chạy định kỳ sẽ cập nhật điểm mới nhất cho toàn hệ thống
        df_output.to_sql("ml_scored_transactions", con=engine, if_exists="replace", index=False)
        print(f"✅ Hoàn thành! Đã lưu kết quả chấm điểm ML vào bảng 'ml_scored_transactions'.")
    except Exception as e:
        print("🔴 Lỗi lưu dữ liệu ML vào DB:", e)

if __name__ == "__main__":
    run_ml_pipeline()