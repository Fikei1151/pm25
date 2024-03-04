from pycaret.regression import *
import pandas as pd
# โหลดข้อมูลที่คุณคลีนแล้ว
data = pd.read_csv('cleaned_101t_data.csv')

# ตรวจสอบว่ามีคอลัมน์ 'DATETIMEDATA' ในข้อมูลหรือไม่
if 'DATETIMEDATA' in data.columns:
    # แปลงคอลัมน์ DATETIMEDATA ให้เป็น datetime
    data['DATETIMEDATA'] = pd.to_datetime(data['DATETIMEDATA'])
    
    # สร้างคอลัมน์ใหม่
    data['hour'] = data['DATETIMEDATA'].dt.hour
    data['day_of_week'] = data['DATETIMEDATA'].dt.dayofweek
    data['day'] = data['DATETIMEDATA'].dt.day
    data['month'] = data['DATETIMEDATA'].dt.month
else:
    print("Column 'DATETIMEDATA' not found in the dataset. Please check your dataset.")

# ตั้งค่าสภาพแวดล้อม PyCaret
exp_reg = setup(data = data, target = 'PM25', session_id=123, 
                ignore_features = ['DATETIMEDATA', 'PM10', 'O3', 'CO', 'NO2', 'SO2', 'WS', 'TEMP', 'RH', 'WD'],
                numeric_features = ['hour', 'day_of_week', 'day', 'month'])

# เปรียบเทียบโมเดล
best_model = compare_models()

# สร้างโมเดล
created_model = create_model(best_model)

# ปรับแต่งโมเดล
tuned_model = tune_model(created_model)

# ประเมินโมเดล
evaluate_model(tuned_model)

# บันทึกโมเดล
save_model(tuned_model, 'final_pm25_prediction_model')
