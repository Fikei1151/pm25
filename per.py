import pandas as pd
from datetime import datetime, timedelta
from pycaret.regression import load_model, predict_model

# สมมติว่าวันสุดท้ายในชุดข้อมูลของคุณคือ '2024-01-02'
last_date_in_dataset = datetime(2024, 3, 3)

# สร้างช่วงเวลาสำหรับ 7 วันข้างหน้า, ทุก ๆ ชั่วโมง
future_dates = [last_date_in_dataset + timedelta(days=i, hours=h) for i in range(1, 8) for h in range(24)]

# สร้าง DataFrame
future_data = pd.DataFrame(future_dates, columns=['DATETIMEDATA'])

# คำนวณ features ที่จำเป็น
future_data['hour'] = future_data['DATETIMEDATA'].dt.hour
future_data['day_of_week'] = future_data['DATETIMEDATA'].dt.dayofweek
future_data['day'] = future_data['DATETIMEDATA'].dt.day
future_data['month'] = future_data['DATETIMEDATA'].dt.month

# ตรวจสอบ future_data
print(future_data.head())


# โหลดโมเดลที่บันทึกไว้
final_model = load_model('final_pm25_prediction_model')

# ทำนายค่า PM2.5 ในอนาคต
predictions = predict_model(final_model, data=future_data)

# แสดงผลลัพธ์การทำนาย
print(predictions)
# บันทึกผลลัพธ์เป็นไฟล์ CSV
predictions.to_csv("predictions.csv", index=False)
