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
    data['DATETIMEDATA'] = pd.to_datetime(data['DATETIMEDATA'])
    last_date_in_dataset = data['DATETIMEDATA'].max()

    # แก้ไข: เริ่มการทำนายจากชั่วโมงถัดไปของข้อมูลสุดท้าย
    start_prediction_datetime = last_date_in_dataset + timedelta(hours=1)
    future_dates = [start_prediction_datetime + timedelta(hours=i) for i in range(168)]  # 168 ชั่วโมง = 7 วัน

    # สร้าง DataFrame
    future_data = pd.DataFrame(future_dates, columns=['DATETIMEDATA'])

    # คำนวณ features ที่จำเป็น
    future_data['hour'] = future_data['DATETIMEDATA'].dt.hour
    future_data['day_of_week'] = future_data['DATETIMEDATA'].dt.dayofweek
    future_data['day'] = future_data['DATETIMEDATA'].dt.day
    future_data['month'] = future_data['DATETIMEDATA'].dt.month

    # โหลดโมเดลที่บันทึกไว้
    final_model = load_model('final_pm25_prediction_model')

    # ทำนายค่า PM2.5 ในอนาคต
    predictions = predict_model(final_model, data=future_data)
    return predictions
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