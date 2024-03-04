import pandas as pd


file_path = 'air4thai_hatyai_stations_data.csv'
data = pd.read_csv(file_path)


data['DATETIMEDATA'] = pd.to_datetime(data['DATETIMEDATA'])

selected_columns = ['DATETIMEDATA', 'PM25', 'WS', 'TEMP', 'RH', 'WD']
cleaned_data = data[selected_columns].copy()  

cleaned_data['PM25'].fillna(cleaned_data['PM25'].mean(), inplace=True)


output_file_path = 'cleaned_data_hatyai.csv'
cleaned_data.to_csv(output_file_path, index=False)

print(output_file_path)