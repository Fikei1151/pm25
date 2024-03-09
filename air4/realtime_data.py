import requests
import pandas as pd
import datetime

def get_station_data(station_id, start_date="2024-01-01"):
    current_datetime = datetime.datetime.now()
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

