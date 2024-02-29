from pycaret.regression import *
import pandas as pd

# ตรวจสอบและแก้ไขเส้นทางไฟล์หรือชื่อไฟล์ตามที่จำเป็น
loaded_model = load_model('final_tuned_model_PM25')  # ถ้าไฟล์อยู่ใน directory เดียวกันกับสคริปต์

# ตัวอย่าง: โหลดข้อมูลพยากรณ์จาก CSV
forecast_data_path = 'cleaned_data_44t_2023-02-19_2024-02-20.csv'  # ปรับเปลี่ยนเส้นทางไฟล์ตามที่ต้องการ
forecast_data = pd.read_csv(forecast_data_path)

predictions = predict_model(loaded_model, data=forecast_data)

# ตรวจสอบชื่อคอลัมน์ทั้งหมดใน predictions DataFrame เพื่อหาชื่อคอลัมน์ทำนาย
print(predictions.columns)

# สมมติว่าชื่อคอลัมน์ที่ถูกต้องคือ 'Score' แทน 'Label'
# และต้องการกรองข้อมูลสำหรับวันที่ 2024-01-27
specific_day_prediction = predictions[predictions['DATETIMEDATA'].str.startswith('2024-01-28')]

# แสดงผลลัพธ์การทำนายสำหรับวันที่ 2024-01-27
print(specific_day_prediction[['DATETIMEDATA', 'prediction_label']])
