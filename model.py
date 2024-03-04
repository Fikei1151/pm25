from pycaret.regression import *
import pandas as pd
# โหลดข้อมูลที่คุณคลีนแล้ว
data = pd.read_csv('cleaned_101t_data.csv')

# ตั้งค่าสภาพแวดล้อม PyCaret
exp_reg101 = setup(data = data, target = 'PM25', session_id=123,
                   ignore_features = ['DATETIMEDATA'],
                   normalize = True, transformation = True, 
                   transform_target = True)

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
