import requests
import pandas as pd

def get_station_data(station_id, start_date="2024-02-28", end_date="2024-02-28"):
    datas = []
    param = "PM25,PM10,O3,CO,NO2,SO2,WS,TEMP,RH,WD"
    data_type = "hr"
    start_time = "00"
    end_time = "23"
    url = f"http://air4thai.com/forweb/getHistoryData.php?stationID={station_id}&param={param}&type={data_type}&sdate={start_date}&edate={end_date}&stime={start_time}&etime={end_time}"
    response = requests.get(url)
    response_json = response.json()
    for data in response_json["stations"][0]["data"]:
        data["stationID"] = response_json["stations"][0]["stationID"]
        datas.append(data)
    return datas

def main(selected_stations=None):
    all_data = []
    if selected_stations:
        for station_id in selected_stations:
            station_data = get_station_data(station_id)
            all_data.extend(station_data)
            print(f"Retrieved data from station: {station_id}")
    else:
        print("No stations specified.")
    
    if all_data:
        pd_from_dict = pd.DataFrame.from_dict(all_data)
        pd_from_dict.to_csv("air4thai_selected_stations_data.csv", index=False)
        print("Data saved to air4thai_selected_stations_data.csv")
    else:
        print("No data retrieved.")

if __name__ == "__main__":
    # ระบุรายการของสถานีตรวจวัดที่ต้องการดึงข้อมูล
    selected_stations = ['59t']  # ตัวอย่าง: ต้องการข้อมูลเฉพาะจากสถานี '62t'
    main(selected_stations=selected_stations)
