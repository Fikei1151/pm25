import pandas as pd
from pycaret.regression import *

# โหลดข้อมูล
data = pd.read_csv('/mnt/data/cleaned_data_44t_2023-02-19_2024-02-20.csv')

# ตั้งค่าสภาพแวดล้อม PyCaret สำหรับการถดถอย
s = setup(data, target='PM2.5', session_id=123)

# เปรียบเทียบโมเดลเบื้องต้นเพื่อหาโมเดลที่ดีที่สุด
best_model = compare_models()

# ปรับแต่งโมเดลที่เลือก
tuned_model = tune_model(best_model)

# ประเมินโมเดล
evaluate_model(tuned_model)

# ทำนายผลด้วยข้อมูลใหม่
predictions = predict_model(tuned_model, data=new_data)