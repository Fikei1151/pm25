import pandas as pd
from datetime import datetime, timedelta
from pycaret.regression import load_model, predict_model

# โหลดชุดข้อมูลของคุณ
data_path = "cleaned_101t_data.csv"  # แทนที่ด้วยเส้นทางไฟล์ของคุณ
data = pd.read_csv(data_path)

# ตรวจสอบว่าคอลัมน์วันที่ในรูปแบบ datetime และคำนวณวันที่สุดท้าย
data['DATETIMEDATA'] = pd.to_datetime(data['DATETIMEDATA'])
last_date_in_dataset = data['DATETIMEDATA'].max()

# แก้ไข: เริ่มการทำนายจากชั่วโมงถัดไปของข้อมูลสุดท้าย
start_prediction_datetime = last_date_in_dataset + timedelta(hours=1)
future_dates = [start_prediction_datetime + timedelta(hours=i) for i in range(168)]  # 168 ชั่วโมง = 7 วัน

# สร้าง DataFrame
future_data = pd.DataFrame(future_dates, columns=['DATETIMEDATA'])

# คำนวณ features ที่จำเป็น
future_data['hour'] = future_data['DATETIMEDATA'].dt.hour
future_data['day_of_week'] = future_data['DATETIMEDATA'].dt.dayofweek
future_data['day'] = future_data['DATETIMEDATA'].dt.day
future_data['month'] = future_data['DATETIMEDATA'].dt.month

# โหลดโมเดลที่บันทึกไว้
final_model = load_model('final_pm25_prediction_model')

# ทำนายค่า PM2.5 ในอนาคต
predictions = predict_model(final_model, data=future_data)

# บันทึกผลลัพธ์เป็นไฟล์ CSV
predictions.to_csv("predictions101.csv", index=False)
