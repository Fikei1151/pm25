from dash import Dash, html, dash_table, dcc, callback, Output, Input
import pandas as pd
import plotly.express as px
import dash_mantine_components as dmc

df = pd.read_csv('cleaned_data_44t_2023-02-19_2024-02-20.csv')

# Initialize the app - incorporate a Dash Mantine theme
external_stylesheets = [dmc.theme.DEFAULT_COLORS]
app = Dash(__name__, external_stylesheets=external_stylesheets)

# App layout
app.layout = dmc.Container([
    dmc.Title('My First App with Data, Graph, and Controls', color="blue", size="h3"),
    dmc.RadioGroup(
            [dmc.Radio(i, value=i) for i in  ['PM25']],
            id='my-dmc-radio-item',
            value='PM25',
            size="sm"
        ),
    dmc.Grid([
        dmc.Col([
            dash_table.DataTable(data=df.to_dict('records'), page_size=12, style_table={'overflowX': 'auto'})
        ], span=6),
        dmc.Col([
            dcc.Graph(figure={}, id='graph-placeholder')
        ], span=6),
    ]),
    dmc.Container(
        "NEXT WEEK PREDICTED", size=200, px=0
        ),           
    
], fluid=True)

# Add controls to build the interaction
@callback(
    Output(component_id='graph-placeholder', component_property='figure'),
    Input(component_id='my-dmc-radio-item', component_property='value')
)
def update_graph(col_chosen):
    fig = px.line(df, x='DATETIMEDATA', y=col_chosen)
    return fig

# Run the App
if __name__ == '__main__':
    app.run(debug=True)