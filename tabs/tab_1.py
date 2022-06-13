import dash
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from dash import dcc, html, dash_table
import pandas as pd
import plotly.io as pio
pio.templates.default="plotly_white"

from helper_functions import calc_index, calc_CAGR, get_balanced_panel, trend_graph, create_table

us_state_to_abbrev={
    "Alabama": "AL",
    "Alaska": "AK",
    "Arizona": "AZ",
    "Arkansas": "AR",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "Delaware": "DE",
    "Florida": "FL",
    "Georgia": "GA",
    "Hawaii": "HI",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Iowa": "IA",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Maine": "ME",
    "Maryland": "MD",
    "Massachusetts": "MA",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Mississippi": "MS",
    "Missouri": "MO",
    "Montana": "MT",
    "Nebraska": "NE",
    "Nevada": "NV",
    "New Hampshire": "NH",
    "New Jersey": "NJ",
    "New Mexico": "NM",
    "New York": "NY",
    "North Carolina": "NC",
    "North Dakota": "ND",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Pennsylvania": "PA",
    "Rhode Island": "RI",
    "South Carolina": "SC",
    "South Dakota": "SD",
    "Tennessee": "TN",
    "Texas": "TX",
    "Utah": "UT",
    "Vermont": "VT",
    "Virginia": "VA",
    "Washington": "WA",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY",
    "District of Columbia": "DC",
    "American Samoa": "AS",
    "Guam": "GU",
    "Northern Mariana Islands": "MP",
    "Puerto Rico": "PR",
    "United States Minor Outlying Islands": "UM",
    "U.S. Virgin Islands": "VI",
}
    
# invert the dictionary
abbrev_to_us_state=dict(map(reversed, us_state_to_abbrev.items()))

# Read data
pop=pd.read_csv('https://raw.githubusercontent.com/garycl/EconApp/master/data/pop.csv')
pop=get_balanced_panel(pop)

# Content
msa_list=pop.loc[pop.Type=='MSA', 'Area'].sort_values().unique()
controls=dbc.Col([
    html.P('Select MSA', style={'textAlign': 'center'}),
    dcc.Dropdown(
        id='msa_dropdown',
        value='New York-Newark-Jersey City, NY-NJ-PA',
        options=[{'label':msa, 'value':msa} for msa in msa_list]
    ),
    html.Br(),
    html.P('Plot Recessions', style={'textAlign': 'center'}),
    dbc.RadioItems(
        id='recession',
        options=[
            {'label':'Yes', 'value':True},
            {'label':'No', 'value':False}
        ],
        value=True,
        inline=True,
        style={'textAlign': 'center'}
    )
])

sidebar=html.Div([
    html.H1(children='Parameters'),
    html.Hr(),
    controls
])

base_df=create_table(pop, 'New York', 'New York-Newark-Jersey City, NY-NJ-PA', 'Population', 'Thousands')
content=html.Div([
    html.Br(),
    dcc.Graph(id='graph-1'),
    html.P('Source: Census Population and Housing'),
    html.Div(id="table-1"),
])

tab_1_layout=html.Div(
    dbc.Row([
        dbc.Col(sidebar, md=3), 
        dbc.Col(content, md=6)
    ])
)

@app.callback(
    Output('graph-1', 'figure'),
    Output('table-1', 'children'),
    Input('msa_dropdown', 'value'),
    Input('recession', 'value')
)

# chart
def display_chart(msa, recession):
        
    if msa is None:
        raise PreventUpdate
    else:
        state_abbrev=msa.split(', ')[1].strip().split('-')[0].strip()
        state_name=abbrev_to_us_state[state_abbrev]

    df=pop[(pop.Area=='United States') | (pop.Area==state_name) | (pop.Area==msa)].copy()
    df=calc_index(df, 'Population')
    df=calc_CAGR(df, 'Index')
        
    x0=df.Year.min()
    fig=trend_graph(
        df, state_name, msa, 'Index', recession,
        title=f"Population Growth Index ({x0} Level=100)",
        xaxis_title="Calendar Year",
        yaxis_title="Index"
    )

    table=create_table(pop, state_name, msa, 'Population', 'Thousands')
    return  fig, dash_table.DataTable(
        columns=[{"name": i, "id": i} for i in table.columns],
        data=table.to_dict('records'),
        fixed_rows={'headers': True},
        style_table={'height': 400},  # defaults to 500
        style_cell={
            'fontSize':16, 
            'font-family':'sans-serif', 
            'textAlign':'right',
        },
        style_header={
            'fontWeight': 'bold', 
        },
        export_format="csv"
    )