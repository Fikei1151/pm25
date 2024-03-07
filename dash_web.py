from dash import dash, html, dash_table, dcc, callback, Output, Input, State
import pandas as pd
import plotly.express as px
import dash_mantine_components as dmc
import datetime
import dash_bootstrap_components as dbc
from pycaret.regression import load_model, predict_model
from datetime import datetime, timedelta

app = dash.Dash(external_stylesheets=[dbc.themes.LUX, 'static/styles.css'])

df = pd.read_csv('cleaned_101t_data.csv')

def generate_predictions():
    data = df.copy()  # ใช้ข้อมูลที่โหลดไว้แล้วใน df
    # ตรวจสอบว่าคอลัมน์วันที่ในรูปแบบ datetime และคำนวณวันที่สุดท้าย
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


    print(predictions.head())

    return predictions


prediction_graph = dbc.Card(
    [
        dbc.CardHeader(html.H5("PM2.5 Predictions")),
        dbc.CardBody([dcc.Graph(id='prediction-graph')])
    ],
    color="light", outline=True, className="board-curved"
)

last_date_in_data = df['DATETIMEDATA'].max()
@app.callback(
    Output('prediction-graph', 'figure'),
    [Input('tabs', 'active_tab')]
)
def update_prediction_graph(active_tab):
    predictions = generate_predictions()
    predictions['DATETIMEDATA'] = pd.to_datetime(predictions['DATETIMEDATA'])
    now = pd.Timestamp(last_date_in_data)
    
    if active_tab == "tab-today":
        filtered_df = predictions[predictions['DATETIMEDATA'].dt.date == now.date()]
    elif active_tab == "tab-3days":
        filtered_df = predictions[predictions['DATETIMEDATA'] >= now - timedelta(days=3)]
    elif active_tab == "tab-7days":
        filtered_df = predictions[predictions['DATETIMEDATA'] >= now - timedelta(days=7)]
    else:
        filtered_df = predictions

    fig = px.line(filtered_df, x='DATETIMEDATA', y='prediction_label', title='PM2.5 Future Predictions')
 
    fig.update_layout(xaxis_title="Date and Time", yaxis_title="Predicted PM2.5")
    return fig




def update_graph():
    fig = px.line(df, x='DATETIMEDATA', y=['PM25'])
    fig.update_layout(
    xaxis_title="Date and Time",  # X-axis label
    yaxis_title="PM2.5",  # Y-axis label
)
    return fig
table = dbc.Card(
    [
        dash_table.DataTable(data=df.to_dict('records'), page_size=5, style_table={'overflowX': 'auto'})
    ], color= 'light', outline= True
)

taps = html.Div(
    dbc.Tabs(
        id="tabs",  # Add an ID to the Tabs for callback
        children=[
            dbc.Tab(label='Today', tab_id="tab-today"),
            dbc.Tab(label='3 Days', tab_id="tab-3days"),
            dbc.Tab(label='7 Days', tab_id="tab-7days"),
        ],
        active_tab="tab-today",
    )
)

line_graph = dbc.Card(
    [
        dbc.CardHeader(taps
        ),
        dbc.CardBody([
            html.H1('Line Graph'),
            dcc.Graph(figure=update_graph(), id='graph-placeholder')
        ]), dbc.CardFooter(table)
    ], color="light", outline= True, className= "board-curved"
)   

search_bar =  dbc.Row([
        dbc.Col(dbc.Input(type="search", placeholder="Start", className= 'board-curved')),
        dbc.Col(dbc.Input(type="search", placeholder="End", className= 'board-curved')),
        dbc.Col(
            dbc.Button(
                "Search", color="primary", className="board-curved", n_clicks=0
            ),
            width="auto",
        ),
    ])


navbar = dbc.Navbar(
    [
        dbc.Col([
                html.H1('BURIRAM', className='text', id='logo'),
                ]),  
        dbc.Collapse(search_bar, className='nav', is_open= True), 
    ],
    color="dark",
    dark=True,
)


app.layout = html.Div(
    [
        dbc.Col(navbar),
        dbc.Row([
            dbc.Col(html.Div(line_graph, className='space-top'), width=6),
            dbc.Col(html.Div(prediction_graph, className='space-top'), width=6)
        ], justify='around')
    ]
)


@app.callback(
    Output('time-update', 'children'),
    [Input('interval-component', 'n_intervals')]
)
def update_value(n_intervals):
    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return dbc.Card([
        dbc.CardBody([
            html.H1(f'{current_time}')
        ])
    ])


@app.callback(
    Output('graph-placeholder', 'figure'),
    [Input('tabs', 'active_tab')]
)
def update_realtime_graph(active_tab):
    df['DATETIMEDATA'] = pd.to_datetime(df['DATETIMEDATA'])
    last_date_in_dataset = df['DATETIMEDATA'].max()
    now = last_date_in_dataset

    if active_tab == "tab-today":
        filtered_df = df[df['DATETIMEDATA'].dt.date == now.date()]
    elif active_tab == "tab-3days":
        filtered_df = df[df['DATETIMEDATA'] >= now - pd.Timedelta(days=3)]
    elif active_tab == "tab-7days":
        filtered_df = df[df['DATETIMEDATA'] >= now - pd.Timedelta(days=7)]
    else:
        filtered_df = df

    fig = px.line(filtered_df, x='DATETIMEDATA', y=['PM25'])
    fig.update_layout(xaxis_title="Date and Time", yaxis_title="Measurement", legend_title="Variable")
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)