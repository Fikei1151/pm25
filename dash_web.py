from dash import dash, html, dash_table, dcc, callback, Output, Input
import pandas as pd
import plotly.express as px
import dash_mantine_components as dmc

import dash_bootstrap_components as dbc
app = dash.Dash(external_stylesheets=[dbc.themes.YETI, 'static/styles.css'])

df = pd.read_csv('cleaned_101t_data.csv')

@app.callback(
    Output(component_id='graph-placeholder', component_property='figure'),
    Input(component_id='my-dmc-radio-item', component_property='value')
)

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

line_graph = dbc.Card(
    [
        dbc.CardBody([
            html.H1('Line Graph'),
            dcc.Graph(figure=update_graph(), id='graph-placeholder')
        ]), dbc.CardFooter(table)
    ], color="light", outline= True, class_name= "board-curved"
)   

app.layout = html.Div(
    [
        html.Div(html.H1('Regression PM 2.5', className= 'bold-text'), className= 'dash'),
        dbc.Row([
            dbc.Col(html.Div(line_graph, className= 'space-top'), width= 5)
        ], justify= 'around')
    ] 
)


if __name__ == '__main__':
    app.run_server(debug=True)