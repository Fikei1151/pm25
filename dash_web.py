from dash import dash, html, dash_table, dcc, callback, Output, Input, State
import pandas as pd
import plotly.express as px
import dash_mantine_components as dmc
import datetime
import dash_bootstrap_components as dbc

app = dash.Dash(external_stylesheets=[dbc.themes.LUX, 'static/styles.css'])

df = pd.read_csv('cleaned_101t_data.csv')

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
            dbc.Tabs([
                dbc.Tab(label = 'today', tab_id="tab-today", active_label_class_name= 'active-text') , 
                dbc.Tab(label = '3 days', tab_id="tab-3days", active_label_class_name= 'active-text') , 
                dbc.Tab(label = '7 days', tab_id="tab-7days", active_label_class_name= 'active-text') 
            ])
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
            dbc.Col(html.Div(line_graph, className= 'space-top'), width=5),
            dbc.Col(html.Div([html.H1(id= 'time-update')]))
        ], justify= 'around')
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



if __name__ == '__main__':
    app.run_server(debug=True)