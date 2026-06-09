import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import os

app = FastAPI(title="Core Banking Transaction Simulator API", version="1.0")

# Đường dẫn tới file dữ liệu Kaggle đã tải
CSV_PATH = "transactions.csv"

class StreamPointer:
    def __init__(self):
        self.current_index = 0
        self.total_rows = 0
        self.df = None

    def load_data(self):
        if not os.path.exists(CSV_PATH):
            raise FileNotFoundError(f"Không tìm thấy file {CSV_PATH}. Vui lòng đổi tên file Kaggle thành transactions.csv")
        # Load trước 200,000 dòng để test (tránh tràn RAM máy cá nhân)
        self.df = pd.read_csv(CSV_PATH, nrows=200000)
        self.total_rows = len(self.df)
        print(f"Đã tải thành công {self.total_rows} dòng dữ liệu.")

pointer = StreamPointer()

@app.on_event("startup")
async def startup_event():
    pointer.load_data()

class TransactionModel(BaseModel):
    step: int
    type: str
    amount: float
    nameOrig: str
    oldbalanceOrg: float
    newbalanceOrig: float
    nameDest: str
    oldbalanceDest: float
    newbalanceDest: float
    isFraud: int

@app.get("/api/v1/transactions/stream", response_model=List[TransactionModel])
async def get_transaction_stream(batch_size: int = 10):
    """Lấy ra 1 lô giao dịch mới mỗi khi được gọi"""
    if pointer.current_index >= pointer.total_rows:
        pointer.current_index = 0 # Đọc hết thì quay lại từ đầu
        
    start = pointer.current_index
    end = min(start + batch_size, pointer.total_rows)
    pointer.current_index = end
    
    batch_df = pointer.df.iloc[start:end]
    return batch_df.to_dict(orient="records")

@app.get("/api/v1/status")
async def get_status():
    return {
        "status": "running",
        "current_pointer": pointer.current_index,
        "total_available_rows": pointer.total_rows
    }