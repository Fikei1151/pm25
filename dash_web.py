from dash import dash, html, dash_table, dcc, callback, Output, Input, State
import pandas as pd
import plotly.express as px
import dash_mantine_components as dmc
import datetime
import dash_bootstrap_components as dbc
from pycaret.regression import load_model, predict_model
from datetime import datetime, timedelta

app = dash.Dash(__name__,suppress_callback_exceptions=True,external_stylesheets=[dbc.themes.LUX, 'static/styles.css'])

df = pd.read_csv('cleaned_101t_data.csv')
df['DATETIMEDATA'] = pd.to_datetime(df['DATETIMEDATA'])


###########################ทำนายค่าpm25######################################
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


#################################################################

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
hiden_table = html.Div(
    [
        dbc.Button(
            "Show Table",
            id="collapse-button",
            className="mb-3",
            color="primary",
            n_clicks=0,
        ),
        dbc.Collapse(
            dbc.Card(dbc.CardBody(table)),
            id="collapse",
            is_open=False,
        ),
    ]
)
@app.callback(
    Output("collapse", "is_open"),
    [Input("collapse-button", "n_clicks")],
    [State("collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

search_bar =  dbc.Row([
        dbc.Col([
            (html.H6('DATE START', className= 'text-start')),
            dbc.Input(type="search", placeholder="YYYY-MM-DD", className= 'board-search', size='sm')]),
        dbc.Col([
            (html.H6('DATE END', className= 'text-start')),
            dbc.Input(type="search", placeholder="YYYY-MM-DD", className= 'board-search', size='sm')]),
        dbc.Col(
            dbc.Button(
                "Search", color="primary", className="button", n_clicks=0, size= 'sm'
            ),
            width="auto",
        ),
    ])

taps = html.Div(
    dbc.Tabs(
        [
            dbc.Tab(label='Today', tab_id="tab-today", tabClassName="ms-auto"),
            dbc.Tab(label='3 Days', tab_id="tab-3days"),
            dbc.Tab(label='7 Days', tab_id="tab-7days"),
        ], id='tabs',
        active_tab="tab-today",
    )
)

line_graph = dbc.Card(
    [
        dbc.CardHeader(html.Div(taps)),
        dbc.CardBody([
            html.Div(search_bar, className='nav'),
            dcc.Graph(figure=update_graph(), id='graph-placeholder', className= 'space-graph'),
            dbc.Row(hiden_table, className= 'table')
        ])
    ], color="dark", outline= True, className= "board-curved"
)   

navbar = dbc.Navbar(
    [
        dbc.Col([
                html.H1('BURIRAM', className='text', id='logo'),
                ]),   
    ],
    color="dark",
    dark=True,
)


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
def calculate_daily_avg_and_color(df):
    # รวมข้อมูลและคำนวณค่าเฉลี่ยรายวัน
    df_daily = df.resample('D', on='DATETIMEDATA').mean().reset_index()
    
    # คำนวณค่าเฉลี่ยและสีสำหรับ 7 วันย้อนหลัง
    df_last_7_days = df_daily.tail(7)
    df_last_7_days['color'] = df_last_7_days['PM25'].apply(determine_pm25_level_color)
    
    return df_last_7_days


# คำนวณและได้ DataFrame ใหม่ที่มีค่าเฉลี่ยและสี
df_daily_avg_color = calculate_daily_avg_and_color(df)

###########################################################################


###########################จัดlayout######################################

app.layout = html.Div([
    dbc.Container(fluid=True, children=[
        # Navbar หรือ Header ของเว็บ
        dbc.Row(
            dbc.Col(navbar, width=12),
            className="mb-3"
        ),
        
        # ส่วนของกราฟ
        dbc.Row([
            dbc.Col(html.Div(line_graph, className='mb-3'), width=6),
            dbc.Col(html.Div(prediction_graph, className='mb-3'), width=6),
        ], justify='around'),
        
        # ส่วนของตาราง
         dbc.Row(
        [
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.H4("PM2.5 Daily Averages - Last 7 Days", className="card-title"),
                        dash_table.DataTable(
                            id='pm25_table',
                            columns=[
                                {"name": "Date", "id": "DATETIMEDATA"},
                                {"name": "PM2.5", "id": "PM25"},
                                {"name": "Air Quality Color", "id": "color", "presentation": "markdown"},
                            ],
                            # ใช้ DataFrame ที่คำนวณค่าเฉลี่ยรายวันและสีแล้ว
                            data=calculate_daily_avg_and_color(df).to_dict('records'),
                            style_data_conditional=[
                                {
                                    'if': {
                                        'column_id': 'color',
                                        'filter_query': '{{color}} = {}'.format(color)
                                    },
                                    'backgroundColor': color,
                                    'color': 'white'
                                } for color in ['blue', 'green', 'yellow', 'orange', 'red', 'purple']
                            ],
                            style_cell={'textAlign': 'center'},
                            style_header={
                                'backgroundColor': 'black',
                                'color': 'white'
                            },
                        ),
                         html.Div(
                            [
                                # สร้างแถบสีด้วย Bootstrap badges หรือคล้ายกับนั้น
                               html.Span("ดี",  className="badge bg-info"),
                                html.Span("ปานกลาง", className="badge bg-success"),
                                html.Span("มีสุขภาพเสี่ยงต่ำ", className="badge bg-warning text-dark"),
                                html.Span("มีสุขภาพเสี่ยง", className="badge bg-danger"),
                                html.Span("มีสุขภาพเสี่ยงสูง", className="badge bg-dark"),
                             
                            ],
                            style={'marginTop': 20, 'display': 'flex', 'justifyContent': 'space-between'}
                        ),
                    ])
                ),
                width=12
            )
        ])
    ])
])

###########################################################################
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