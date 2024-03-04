import pandas as pd
from pycaret.regression import load_model, predict_model
from datetime import datetime, timedelta

# โหลดโมเดลที่ฝึกสำเร็จแล้ว
model = load_model('final_pm25_prediction_model')

# โหลดข้อมูลล่าสุดที่คุณมี
latest_data = pd.read_csv('cleaned_101t_data.csv')

# กำหนดเวลาเริ่มต้นสำหรับการทำนาย ตัวอย่างเช่น, เวลาล่าสุดในข้อมูลของคุณ
start_datetime = datetime.strptime(latest_data['DATETIMEDATA'].iloc[-1], '%Y-%m-%d %H:%M:%S')

# สร้าง DataFrame เพื่อเก็บผลการทำนาย
predictions = pd.DataFrame()

# สมมติว่า latest_data มีข้อมูลที่ต้องการทั้งหมดและเรียงลำดับตามเวลาอยู่แล้ว

# วนลูปทำนายค่า PM2.5 สำหรับ 168 ชั่วโมง (7 วัน)
for i in range(168):
    # อัปเดตเวลาสำหรับข้อมูลในการทำนาย
    current_datetime = start_datetime + timedelta(hours=i)
    
    # สร้างข้อมูลอินพุตใหม่สำหรับการทำนายโดยใช้ข้อมูลล่าสุด
    # โปรดปรับส่วนนี้ให้เหมาะสมกับโครงสร้างข้อมูลและโมเดลของคุณ
    input_data = latest_data.copy()
    input_data['DATETIMEDATA'] = current_datetime.strftime('%Y-%m-%d %H:%M:%S')
    
    # ทำนายค่า PM2.5 สำหรับชั่วโมงถัดไป
    prediction = predict_model(model, data=input_data)
    prediction['DATETIMEDATA'] = current_datetime.strftime('%Y-%m-%d %H:%M:%S')
    
    # เพิ่มผลการทำนายลงใน predictions DataFrame
    predictions = pd.concat([predictions, prediction], ignore_index=True)
    
    # อัปเดต latest_data ด้วยข้อมูลที่ทำนายได้สำหรับการทำนายถัดไป (หากจำเป็น)
    # คุณอาจต้องปรับแต่งส่วนนี้ให้เข้ากับโครงสร้างข้อมูลของคุณ

# พิมพ์หรือบันทึกผลการทำนาย
print(predictions)
# predictions.to_csv('pm25_predictions_for_next_7_days.csv', index=False)
