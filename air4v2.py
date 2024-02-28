import requests
import pandas as pd

def get_station_data(station_id, start_date="2024-02-26", end_date="2024-02-27"):
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

def get_station_id():
    station_ids_url = "http://air4thai.com/forweb/getHistoryStation.php"
    response = requests.get(station_ids_url)
    response_json = response.json()
    station_ids = [(i["ID"], i["Area"]) for i in response_json]
    return station_ids

def main(max_stations=None):
    station_ids = get_station_id()
    all_data = []
    for i, station in enumerate(station_ids[:max_stations]):
        station_data = get_station_data(station[0])
        all_data.extend(station_data)
        print(f"Retrieved data from station: {station[0]} ({station[1]})")
    
    if all_data:
        pd_from_dict = pd.DataFrame.from_dict(all_data)
        pd_from_dict.to_csv("air4thai_combined_data.csv", index=False)
        print("Data saved to air4thai_combined_data.csv")
    else:
        print("No data retrieved.")

if __name__ == "__main__":

    main(max_stations=86)  
