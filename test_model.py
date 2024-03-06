import pandas as pd
from datetime import datetime, timedelta
from pycaret.regression import load_model, predict_model

# โหลดชุดข้อมูลของคุณ
data_path = "/dataclean/cleaned_100t_data.csv"  # แทนที่ด้วยเส้นทางไฟล์ของคุณ
data = pd.read_csv(data_path)

# ตรวจสอบว่าคอลัมน์วันที่ในรูปแบบ datetime และคำนวณวันที่สุดท้าย
data['DATETIMEDATA'] = pd.to_datetime(data['DATETIMEDATA'])
last_date_in_dataset = data['DATETIMEDATA'].max()

# สร้างช่วงเวลาสำหรับ 7 วันข้างหน้า, ทุก ๆ ชั่วโมง
future_dates = [last_date_in_dataset + timedelta(days=i, hours=h) for i in range(1, 8) for h in range(24)]

# สร้าง DataFrame
future_data = pd.DataFrame(future_dates, columns=['DATETIMEDATA'])

# คำนวณ features ที่จำเป็น
future_data['hour'] = future_data['DATETIMEDATA'].dt.hour
future_data['day_of_week'] = future_data['DATETIMEDATA'].dt.dayofweek
future_data['day'] = future_data['DATETIMEDATA'].dt.day
future_data['month'] = future_data['DATETIMEDATA'].dt.month

# โหลดโมเดลที่บันทึกไว้
final_model = load_model('final_pm25_prediction100_model')

# ทำนายค่า PM2.5 ในอนาคต
predictions = predict_model(final_model, data=future_data)

# บันทึกผลลัพธ์เป็นไฟล์ CSV
predictions.to_csv("predictions100.csv", index=False)
