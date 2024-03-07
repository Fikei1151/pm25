import pandas as pd

# โหลดข้อมูล
file_path = 'data/air4thai_101t_stations_data.csv'  # แก้ไขเส้นทางไฟล์ข้อมูลของคุณ
data = pd.read_csv(file_path)

# คำนวณค่าเฉลี่ยสำหรับคอลัมน์ที่มีข้อมูลหาย
mean_values = data[['O3', 'CO', 'NO2', 'SO2']].mean()

# แทนที่ค่าข้อมูลที่หายไปด้วยค่าเฉลี่ย
data_filled = data.fillna(mean_values)

# ลบแถวที่คอลัมน์ `PM25` มีค่าหายไป
data_cleaned = data_filled.dropna(subset=['PM25'])

# ลบคอลัมน์ `stationID`
data_cleaned = data_cleaned.drop(columns=['stationID'])

# ตรวจสอบโครงสร้างข้อมูลหลังจากการคลีน
print(data_cleaned.info())
print(data_cleaned.head())
new_file_path = 'cleaned_101t_data.csv'  # คุณสามารถเปลี่ยนชื่อไฟล์ได้ตามต้องการ
data_cleaned.to_csv(new_file_path, index=False)

print(f"Data cleaned and saved to {new_file_path}")