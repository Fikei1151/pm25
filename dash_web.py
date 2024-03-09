from dash import dash, html, dash_table, dcc, callback, Output, Input, State
import pandas as pd
import plotly.express as px
import datetime
import dash_bootstrap_components as dbc
from pycaret.regression import load_model, predict_model
from datetime import datetime, timedelta
from air4 import realtime_data

app = dash.Dash(__name__,suppress_callback_exceptions=True,external_stylesheets=[dbc.themes.LUX, 'static/styles.css'])

navbar = dbc.Navbar(
    [
        dbc.Col([
                html.H1('BURIRAM', className='text', id='logo'),
                ]),   
    ],
    color="dark",
    dark=True,
)

search_bar = dbc.Row([
    dbc.Col([
        html.H6('DATE START', className='text-start'),
        dbc.Input(id='start_date', type="search", placeholder="YYYY-MM-DD", className='board-search', size='sm')]),
    dbc.Col([
        html.H6('DATE END', className='text-start'),
        dbc.Input(id='end_date', type="search", placeholder="YYYY-MM-DD", className='board-search', size='sm')]),
    dbc.Col(
        dbc.Button("Search", id='search-button', color="primary", className="button", n_clicks=0, size='sm'),
            width="auto",),
    ])

taps = dbc.Tabs(
        [
            dbc.Tab(label='Today', tab_id="tab-today", active_label_class_name='active-text', tab_class_name='tap', label_class_name='label-tap'),
            dbc.Tab(label='3 Days', tab_id="tab-3days", active_label_class_name='active-text', tab_class_name='tap', label_class_name='label-tap'),
            dbc.Tab(label='7 Days', tab_id="tab-7days", active_label_class_name='active-text', tab_class_name='tap', label_class_name='label-tap'),
            dbc.Tab(label='search', tab_id="tab-search", active_label_class_name='active-text', tab_class_name='tap', label_class_name='label-tap'),
        ], id='tabs',
        active_tab="tab-today",
    )

taps_predic = dbc.Tabs(
        [
            dbc.Tab(label='Today', tab_id="pre-today", active_label_class_name='active-text', tab_class_name='tap', label_class_name='label-tap'),
            dbc.Tab(label='Next 3 Days', tab_id="pre-3days", active_label_class_name='active-text', tab_class_name='tap', label_class_name='label-tap'),
            dbc.Tab(label='Next 7 Days', tab_id="pre-7days", active_label_class_name='active-text', tab_class_name='tap', label_class_name='label-tap'),
        ], id='tabs_predict',
        active_tab="pre-7days",
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
            (html.Div(id='table_realtime')),
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

hiden_predict_table = html.Div(
    [
        dbc.Button(
            "Show Table",
            id="collapse-button-pre",
            className="mb-3",
            color="primary",
            n_clicks=0,
        ),
        dbc.Collapse(
            (html.Div(id='table_realtime_pre')),
            id="collapse-pre",
            is_open=False,
        ),
    ]
)
@app.callback(
    Output("collapse-pre", "is_open"),
    [Input("collapse-button-pre", "n_clicks")],
    [State("collapse-pre", "is_open")],
)
def toggle_collapse_pre(n, is_open):
    if n:
        return not is_open
    return is_open
###########################ทำนายค่าpm25######################################

prediction_graph = dbc.Card(
    [
        dbc.CardHeader(taps_predic),
        dbc.CardBody([
            dcc.Interval(
                id='interval-pre',interval=1000*60, n_intervals=0 ),
            dbc.Row(html.H4("PM2.5 PREDICTIONS"), className='predic'),
            dcc.Graph(id= 'prediction-graph'),
            dbc.Row(hiden_predict_table, className= 'table')
        ])
    ], color='dark', outline=True, className= 'board-curved'
)

@app.callback(
    Output('prediction-graph', 'figure'),
    Output('table_realtime_pre', 'children'),
    [Input('tabs_predict', 'active_tab')],
    [State('interval-pre', 'n_intervals')]
)

def update_prediction_graph(active_tab, n_intervals):
    df = realtime_data.main()
    last_date_in_data = df['DATETIMEDATA'].max()
    predictions = realtime_data.generate_predictions()
    predictions['DATETIMEDATA'] = pd.to_datetime(predictions['DATETIMEDATA'])
    now = predictions['DATETIMEDATA'].min()
    
    if active_tab == "pre-today":
        filtered_df = predictions[predictions['DATETIMEDATA'].dt.date == now.date()]
    elif active_tab == "pre-3days":
        filtered_df = predictions[predictions['DATETIMEDATA'] <= now + timedelta(days=3)]
    elif active_tab == "pre-7days":
        filtered_df = predictions[predictions['DATETIMEDATA'] <= now + timedelta(days=7)]
    else:
        filtered_df = predictions
    fig = px.line(filtered_df, x='DATETIMEDATA', y='prediction_label')
    fig.update_layout(xaxis_title="Date and Time", yaxis_title="Predicted PM2.5")

    ###befor show on table #####
    filtered_df['prediction_label'] = filtered_df['prediction_label'].round(decimals=2)
    filtered_df['DATETIMEDATA'] = filtered_df['DATETIMEDATA'].dt.strftime('%a %m %y')
    table_predict = dbc.Card([
        dash_table.DataTable(data=filtered_df.to_dict('records'), page_size=4)], color= 'light', outline= False)
    return fig, table_predict


#################################################################

line_graph = dbc.Card(
    [
        dbc.CardHeader(
            dbc.Col(taps, style={"margin-left": "0px"})),
        dbc.CardBody([
            dcc.Interval(
                id='interval-component',interval=1000*60, n_intervals=0 ),
            dbc.Row(
                dbc.Collapse(dbc.Row(search_bar), is_open= False, id='show-search-bar')
            ),
            dbc.Row(html.H4("PM2.5 HISTORY"), className='realtime'),
            dcc.Graph(id='graph-placeholder', className= ''),
            dbc.Row(hiden_table, className= 'table')
        ])
    ], color="dark", outline= True, className= "board-curved"
)
@app.callback(
    Output('show-search-bar', 'is_open'),
    [Input('tabs', 'active_tab')],
    [State('show-search-bar', 'is_open')]
) 
def tap_search(active_tab, is_open):
    if active_tab == "tab-search":
        return not is_open
    
@app.callback(
    Output('graph-placeholder', 'figure'),
    Output('table_realtime', 'children'),
    [Input('tabs', 'active_tab')],
    [Input('search-button', 'n_clicks')],
    [State('start_date', 'value')],
    [State('end_date', 'value')],
    [State('interval-component', 'n_intervals')]
)
def update_realtime_graph(active_tab, n_clicks, start_date, end_date, n_intervals):
    df = realtime_data.main()
    df['DATETIMEDATA'] = pd.to_datetime(df['DATETIMEDATA'])
    last_date_in_dataset = df['DATETIMEDATA'].max()
    now = last_date_in_dataset
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    if active_tab == "tab-today":
        filtered_df = df[df['DATETIMEDATA'].dt.date == now.date()]
    elif active_tab == "tab-3days":
        filtered_df = df[df['DATETIMEDATA'] >= now - pd.Timedelta(days=3)]
    elif active_tab == "tab-7days":
        filtered_df = df[df['DATETIMEDATA'] >= now - pd.Timedelta(days=7)]
    elif active_tab == "tab-search" and n_clicks:
        if start_date == end_date:
            filtered_df = df[df['DATETIMEDATA'].dt.date == start_date.date()]
        elif start_date <= now and end_date <= now:
            filtered_df = df[(df['DATETIMEDATA'] >= start_date) & (df['DATETIMEDATA'] <= end_date)]
        else:
            filtered_df = df
    else:
        filtered_df = df
    fig = px.line(filtered_df, x='DATETIMEDATA', y=['PM25'])
    fig.update_layout(xaxis_title="Date and Time", yaxis_title="PM2.5", legend_title="Variable")

    ###befor show on table #####
    filtered_df['DATETIMEDATA'] = filtered_df['DATETIMEDATA'].dt.strftime('%a %m %y')

    table_rt = dbc.Card([
        dash_table.DataTable(
            data=filtered_df.to_dict('records'), page_size=8)], color= 'light', outline= False)
    return fig, table_rt

# คำนวณและได้ DataFrame ใหม่ที่มีค่าเฉลี่ยและสี
last7days_table = dbc.Card(
                    dbc.CardBody([
                        dbc.Row(html.H4("PM2.5 Daily Averages - Last 7 Days"), className='pmlastweek'),
                        dash_table.DataTable(
                            id='pm25_table',
                            columns=[
                                {"name": "Date", "id": "DATETIMEDATA"},
                                {"name": "PM2.5", "id": "PM25"},
                                {"name": "Air Quality Color", "id": "color", "presentation": "markdown"},
                            ],
                            # ใช้ DataFrame ที่คำนวณค่าเฉลี่ยรายวันและสีแล้ว
                            data=realtime_data.calculate_daily_avg_and_color().to_dict('records'),
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
                    ]), color='dark', outline=True, className= 'board-curved'
                )

###########################จัดlayout######################################

app.layout = html.Div([
        dbc.Row(
            dbc.Col(navbar),
            className="mb-3"
        ),
        
        # ส่วนของกราฟ
        dbc.Row([
            dbc.Col(
                html.Div(line_graph, className='space-top'), width=5),
            dbc.Col(
                dbc.Row(
                    [
                        html.Div(prediction_graph),
                        html.Div(last7days_table, className='space-top')
                    ], className='space-top'), width=5),
        ], justify='around'),
])

###########################################################################
if __name__ == '__main__':
    app.run_server(debug=True)