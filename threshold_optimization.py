import pandas as pd
import numpy as np
from sqlalchemy import create_engine

# --- CẤU HÌNH POSTGRESQL ---
DB_URL = "postgresql://postgres:anhquan26@localhost:5432/fraud_db"
engine = create_engine(DB_URL)

# --- THÔNG SỐ CHI PHÍ KINH DOANH (GIẢ ĐỊNH) ---
COST_BURDEN_FP = 20.0       # Chi phí xử lý khiếu nại + mất niềm tin khi chặn nhầm 1 khách hàng thật
COST_BURDEN_FN = 500.0      # Chi phí tổn thất trung bình khi để lọt lưới 1 vụ gian lận

def evaluate_thresholds():
    print("📈 ĐANG PHÂN TÍCH TỐI ƯU HÓA NGƯỠNG CHI PHÍ...")
    
    # Định nghĩa danh sách các mức ngưỡng số tiền cần kiểm tra để tìm điểm tối ưu
    threshold_candidates = [10000, 50000, 100000, 250000, 500000, 1000000, 2000000]
    
    results = []
    
    for T in threshold_candidates:
        # Câu lệnh SQL phân loại giao dịch dựa trên nhãn thực tế 'isFraud' của Kaggle
        query = f"""
        SELECT 
            COUNT(CASE WHEN amount > {T} AND "isFraud" = 1 THEN 1 END) as tp,
            COUNT(CASE WHEN amount > {T} AND "isFraud" = 0 THEN 1 END) as fp,
            COUNT(CASE WHEN amount <= {T} AND "isFraud" = 1 THEN 1 END) as fn
        FROM raw_transactions;
        """
        
        df_metrics = pd.read_sql(query, engine)
        tp = int(df_metrics['tp'].iloc[0])
        fp = int(df_metrics['fp'].iloc[0])
        fn = int(df_metrics['fn'].iloc[0])
        
        # Hàm mục tiêu: Tính toán tổng thiệt hại tài chính tại mức ngưỡng T
        total_cost = (fp * COST_BURDEN_FP) + (fn * COST_BURDEN_FN)
        
        # Tính toán tỷ lệ báo động giả (False Positive Rate)
        fpr = fp / (fp + tp) if (fp + tp) > 0 else 0
        
        results.append({
            "Ngưỡng (T)": T,
            "Bắt đúng (TP)": tp,
            "Chặn nhầm (FP)": fp,
            "Lọt lưới (FN)": fn,
            "Tỷ lệ báo động giả (FPR)": f"{fpr:.2%}",
            "Tổng chi phí tổn thất ($)": total_cost
        })
        
    df_results = pd.DataFrame(results)
    
    print("\n📊 BẢNG SO SÁNH HIỆU QUẢ CÁC MỨC NGƯỠNG:")
    print(df_results.to_string(index=False))
    
    # Tìm mức ngưỡng có chi phí thấp nhất
    best_row = df_results.loc[df_results["Tổng chi phí tổn thất ($)"].idxmin()]
    print("\n💡 KHUYẾN NGHỊ TỪ DATA ANALYST:")
    print(f"-> Mức ngưỡng tối ưu nhất cho hệ thống là: {best_row['Ngưỡng (T)']} USD")
    print(f"-> Giúp tối thiểu hóa tổng chi phí tổn thất xuống còn: {best_row['Tổng chi phí tổn thất ($)']} USD")

if __name__ == "__main__":
    evaluate_thresholds()