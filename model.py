from pycaret.regression import *
import pandas as pd

# ตัวอย่าง: โหลดข้อมูลของคุณ
# ต้องแก้ไขเส้นทางไฟล์ตามที่คุณมี
data_path = 'cleaned_data_44t_2023-02-19_2024-02-20.csv'
data = pd.read_csv(data_path)

# ตั้งค่าสภาพแวดล้อม PyCaret สำหรับการวิเคราะห์การถดถอย
exp_reg = setup(data=data, target='PM25', session_id=123,
                normalize=True, transformation=True, transform_target=True)

# เปรียบเทียบโมเดลหลายๆ ตัวเพื่อหาโมเดลที่ดีที่สุด
best_model = compare_models()

# ปรับแต่งโมเดลที่เลือก
tuned_model = tune_model(best_model, optimize = 'RMSE')

# ประเมินโมเดลที่ปรับแต่งแล้ว
evaluate_model(tuned_model)

# ทำนายผลลัพธ์ในชุดข้อมูลทดสอบ
predictions = predict_model(tuned_model)

save_model(tuned_model, 'final_tuned_model_PM25')

# พิมพ์ผลลัพธ์การทำนาย
print(predictions.head())
