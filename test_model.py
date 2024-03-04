import pandas as pd
from pycaret.regression import load_model, predict_model
from datetime import datetime, timedelta

# โหลดโมเดลที่ฝึกสำเร็จแล้ว
model = load_model('final_pm25_prediction_model')

# โหลดข้อมูลล่าสุดที่คุณมี
latest_data = pd.read_csv('cleaned_101t_data.csv')

# กำหนดเวลาเริ่มต้นสำหรับการทำนาย
start_datetime = datetime.strptime(latest_data['DATETIMEDATA'].iloc[-1], '%Y-%m-%d %H:%M:%S') + timedelta(hours=1)  # เริ่มจากชั่วโมงถัดไป

# สร้าง DataFrame เพื่อเก็บผลการทำนาย
predictions = pd.DataFrame()

# ตั้งค่าเพื่อตรวจสอบเวลาที่ถูกเพิ่มแล้ว
added_times = set()

# วนลูปทำนายค่า PM2.5 สำหรับ 168 ชั่วโมง (7 วัน)
for i in range(168):
    # อัปเดตเวลาสำหรับข้อมูลในการทำนาย
    current_datetime = start_datetime + timedelta(hours=i)
    formatted_datetime = current_datetime.strftime('%Y-%m-%d %H:%M:%S')
    print(f"Adding prediction for {formatted_datetime}")
    # ตรวจสอบว่าเวลานี้ถูกเพิ่มแล้วหรือไม่
    if formatted_datetime in added_times:
        continue  # ถ้าเพิ่มแล้ว, ข้ามการทำนายนี้
    added_times.add(formatted_datetime)  # บันทึกเวลาที่เพิ่ม
    
    # สร้างข้อมูลอินพุตใหม่สำหรับการทำนาย
    input_data = latest_data.tail(24).copy()  # ใช้ข้อมูล 24 ชั่วโมงล่าสุด
    input_data['DATETIMEDATA'] = formatted_datetime
   
    # ทำนายค่า PM2.5 สำหรับชั่วโมงถัดไป
    prediction = predict_model(model, data=input_data)
    prediction['DATETIMEDATA'] = formatted_datetime
    
    # เพิ่มผลการทำนายลงใน predictions DataFrame
    predictions = pd.concat([predictions, prediction[['DATETIMEDATA', 'prediction_label']]], ignore_index=True)
    
# พิมพ์หรือบันทึกผลการทำนาย
print(predictions)
predictions.to_csv('pm25_predictions_for_next_7_days.csv', index=False)

