# import pandas as pd
# from datetime import datetime, timedelta

# # สมมติว่าวันสุดท้ายในข้อมูลคือ 2024-01-02
# last_date = datetime(2024, 3, 3)

# # สร้างช่วงเวลาสำหรับ 7 วันข้างหน้า, ทุก ๆ ชั่วโมง
# future_dates = [last_date + timedelta(days=i, hours=h) for i in range(1, 8) for h in range(24)]

# # สร้าง DataFrame จากช่วงเวลานี้
# future_data = pd.DataFrame(future_dates, columns=['DATETIMEDATA'])

# # คำนวณ features ที่จำเป็น
# future_data['hour'] = future_data['DATETIMEDATA'].dt.hour
# future_data['day_of_week'] = future_data['DATETIMEDATA'].dt.dayofweek
# future_data['day'] = future_data['DATETIMEDATA'].dt.day
# future_data['month'] = future_data['DATETIMEDATA'].dt.month

# # ตัวอย่างข้อมูลที่จะใช้ในการทำนาย
# future_data.head()
import pandas as pd

# โหลดข้อมูล
data_path = 'cleaned_101t_data.csv'  # แก้ไขเป็น path ของไฟล์ข้อมูลของคุณ
data = pd.read_csv(data_path)

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

# ตรวจสอบคอลัมน์ใหม่
print(data.head())
