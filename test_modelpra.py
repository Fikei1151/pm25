import pandas as pd
from datetime import datetime, timedelta
from pycaret.regression import load_model, predict_model

# โหลดชุดข้อมูลของคุณ
data_path = "cleaned_101t_data.csv"  # แทนที่ด้วยเส้นทางไฟล์ของคุณ
data = pd.read_csv(data_path)

# ตรวจสอบว่าคอลัมน์วันที่ในรูปแบบ datetime และคำนวณวันที่สุดท้าย
data['DATETIMEDATA'] = pd.to_datetime(data['DATETIMEDATA'])
last_date_in_dataset = data['DATETIMEDATA'].max()


start_date = last_date_in_dataset + timedelta(hours=1)
future_dates = [start_date + timedelta(hours=i) for i in range(0, 168)]  # สร้างช่วงเวลา 7 วัน (24*7=168 ชั่วโมง)

future_data = pd.DataFrame(future_dates, columns=['DATETIMEDATA'])
future_data['hour'] = future_data['DATETIMEDATA'].dt.hour
future_data['day_of_week'] = future_data['DATETIMEDATA'].dt.dayofweek
future_data['day'] = future_data['DATETIMEDATA'].dt.day
future_data['month'] = future_data['DATETIMEDATA'].dt.month

# ลิสต์ของพารามิเตอร์ที่ต้องทำนาย
parameters = ['NO2', 'SO2', 'WS', 'TEMP', 'RH', 'WD']

# โหลดแต่ละโมเดลทำนายพารามิเตอร์และใส่ค่าทำนายกลับไปยัง future_data
for param in parameters:
    model = load_model(f'final_{param}_prediction_model')

    predictions = predict_model(model, data=future_data)
    future_data[param] = predictions['prediction_label']  # ใช้ชื่อคอลัมน์ต้นฉบับ

# โหลดโมเดลทำนาย PM2.5
pm25_model = load_model('final_pm25_predictionGod_model')

# เตรียมข้อมูลสำหรับโมเดล PM2.5
# เตรียมข้อมูลสำหรับโมเดล PM2.5 โดยรวมคอลัมน์ที่ต้องการ
input_data_for_pm25 = future_data[['NO2', 'SO2', 'WS', 'TEMP', 'RH', 'WD', 'hour', 'day_of_week', 'day', 'month']]

# ทำนายค่า PM2.5
pm25_predictions = predict_model(pm25_model, data=input_data_for_pm25)

# เพิ่มค่าทำนาย PM2.5 กลับเข้าไปใน future_data
future_data['predicted_PM2.5'] = pm25_predictions['prediction_label']

# บันทึกผลลัพธ์เป็น CSV
future_data.to_csv("PM2.5_future_predictions.csv", index=False)

print("Prediction completed and saved to PM2.5_future_predictions.csv")
