import requests
import pandas as pd
from datetime import datetime, timedelta
from pycaret.regression import load_model, predict_model

def get_station_data(station_id, start_date="2024-01-01"):
    current_datetime = datetime.now()
    end_date = current_datetime.strftime("%Y-%m-%d")
    datas = []
    param = "PM25,PM10,O3,CO,NO2,SO2,WS,TEMP,RH,WD"
    data_type = "hr"
    start_time = "00"
    end_time = "23"
    url = f"http://air4thai.com/forweb/getHistoryData.php?stationID=101t&param={param}&type={data_type}&sdate={start_date}&edate={end_date}&stime={start_time}&etime={end_time}"
    response = requests.get(url)
    response_json = response.json()
    for data in response_json["stations"][0]["data"]:
        data["stationID"] = response_json["stations"][0]["stationID"]
        datas.append(data)
    return datas

def main():
    selected_stations= ['101t']
    all_data = []
    if selected_stations:
        for station_id in selected_stations:
            station_data = get_station_data(station_id)
            all_data.extend(station_data)    
    if all_data:
        pd_from_dict = pd.DataFrame.from_dict(all_data)
        pd_from_dict = pd_from_dict.drop(columns='stationID')
        mean_values = pd_from_dict[['O3', 'CO', 'NO2', 'SO2']].mean()
        pd_from_dict = pd_from_dict.fillna(mean_values.round(decimals=2))
        return pd_from_dict
    else:
        print("No data retrieved.")

#############  DATA   FRAME  LIVE UPDATE ##############
df = main()
df['DATETIMEDATA'] = pd.to_datetime(df['DATETIMEDATA'])
#####################################################


def generate_predictions():
    data = df
    # ตรวจสอบว่าคอลัมน์วันที่ในรูปแบบ datetime และคำนวณวันที่สุดท้าย
    data['DATETIMEDATA'] = pd.to_datetime(data['DATETIMEDATA'])
    last_date_in_dataset = data['DATETIMEDATA'].max()


    start_date = last_date_in_dataset + timedelta(hours=1)
    future_dates = [start_date + timedelta(hours=i) for i in range(0, 168)]  

    future_data = pd.DataFrame(future_dates, columns=['DATETIMEDATA'])
    future_data['hour'] = future_data['DATETIMEDATA'].dt.hour
    future_data['day_of_week'] = future_data['DATETIMEDATA'].dt.dayofweek
    future_data['day'] = future_data['DATETIMEDATA'].dt.day
    future_data['month'] = future_data['DATETIMEDATA'].dt.month

    # โหลดและทำนายด้วยโมเดลพารามิเตอร์ต่างๆ
    parameters = ['NO2', 'SO2', 'WS', 'TEMP', 'RH', 'WD']
    for param in parameters:
        model = load_model(f'final_{param}_prediction_model')
        predictions = predict_model(model, data=future_data)
        future_data[param] = predictions['prediction_label']  # อาจต้องปรับเปลี่ยนชื่อคอลัมน์ของค่าทำนายให้ตรงกับที่โมเดลส่งกลับมา

    # โหลดโมเดลทำนาย PM2.5 และทำนายค่า PM2.5
    pm25_model = load_model('final_pm25_predictionGod_model')
    input_data_for_pm25 = future_data[['NO2', 'SO2', 'WS', 'TEMP', 'RH', 'WD', 'hour', 'day_of_week', 'day', 'month']]
    pm25_predictions = predict_model(pm25_model, data=input_data_for_pm25)
    future_data['prediction_label'] = pm25_predictions['prediction_label']  # อาจต้องปรับเปลี่ยนชื่อคอลัมน์ของค่าทำนายให้ตรงกับที่โมเดลส่งกลับมา

    # คืนค่าเฉพาะคอลัมน์วันที่และค่า PM2.5 ที่ทำนายได้
    return future_data[['DATETIMEDATA', 'prediction_label']]
###########################เฉลี่ยตารางข้อมูล######################################
def determine_pm25_level_color(value):
    if value <= 12:
        return 'blue'  # ดี
    elif value <= 35.4:
        return 'green'  # ปานกลาง
    elif value <= 55.4:
        return 'orange'  # มีสุขภาพเสี่ยงต่ำ
    elif value <= 150.4:
        return 'red'  # มีสุขภาพเสี่ยง
    elif value <= 250.4:
        return 'purple'  # มีสุขภาพเสี่ยงสูง
    else:
        return 'purple'  # อันตราย
# ฟังก์ชันสำหรับการคำนวณค่าเฉลี่ย PM2.5 รายวันย้อนหลัง 7 วัน
def calculate_daily_avg_and_color(df=df):
    # รวมข้อมูลและคำนวณค่าเฉลี่ยรายวัน
    df_daily = df.resample('D', on='DATETIMEDATA').mean().round(decimals=2).reset_index()
    # คำนวณค่าเฉลี่ยและสีสำหรับ 7 วันย้อนหลัง
    df_last_7_days = df_daily.tail(7)
    df_last_7_days['color'] = df_last_7_days['PM25'].apply(determine_pm25_level_color)
    ###befor show on table #####
    df_last_7_days['DATETIMEDATA'] = df_last_7_days['DATETIMEDATA'].dt.strftime('%a %m %y')
    return df_last_7_days