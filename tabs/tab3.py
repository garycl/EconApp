import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
import pandas as pd

# Sidebar Style
SIDEBAR_STYLE={
    'position': 'fixed',
    'top': 0,
    'left': 0,
    'bottom': 0,
    'width': '20%',
    'padding': '20px 10px',
    'background-color': '#f8f9fa'
}

# Content Style
CONTENT_STYLE={
    'float':'left',
    'margin-left':'5%',
    'margin-right':'5%',
    'top': 0,
    'padding': '20px 10px'
}

# Read data
def create_layout(data):

    msa_list=(
        data.
        loc[(data.Type!='Nation')&(data.Type!='State'), 'Area']
        .sort_values()
        .unique()
    )

    # Layout
    controls=dbc.Col([
        html.H5('Select MSA', style={'textAlign': 'center'}),
        dcc.Dropdown(
            id='area_dropdown',
            value='New York-Newark-Jersey City, NY-NJ-PA',
            options=[{'label':msa, 'value':msa} for msa in msa_list]
        ),
        dcc.Dropdown(
            id='yvar_dropdown',
            value='Real GDP (Millions)',
            options=[{'label':yvar, 'value':yvar} for yvar in ['Real GDP (Millions)', 'Real Per Capita Personal Income']]
        ),
        html.Br(),
        html.H5('Plot Recessions', style={'textAlign': 'center'}),
        dbc.RadioItems(
            id='recession',
            options=[
                {'label':'Yes', 'value':True},
                {'label':'No', 'value':False}
            ],
            value=True,
            inline=True,
            style={'textAlign': 'center'}
        ),
        html.Br(),
        # US annotation
        html.P(
            'Adjust U.S. Annotation',
            style={
                'textAlign':'center',
                'color': '#1b9e77',
                'font-weight':'bolder', 
                'margin-bottom': '0px'
            }
        ),
        dbc.RadioItems(
            id='nation_adj-3',
            options=[
                {'label':'Up', 'value':True},
                {'label':'Down', 'value':False}
            ],
            value=True,
            inline=True,
            style={'textAlign': 'center'}
        ),
        dcc.Slider(
            min=0, 
            max=5, 
            step=.5, 
            value=0, 
            id='nation_slider-3'
        ),
        # State annotation
        html.P(
            'Adjust State Annotation',
            style={
                'textAlign':'center',
                'color': '#7570b3', 
                'font-weight':'bolder', 
                'margin-bottom': '0px'
            }
        ),
        dbc.RadioItems(
            id='state_adj-3',
            options=[
                {'label':'Up', 'value':True},
                {'label':'Down', 'value':False}
            ],
            value=True,
            inline=True,
            style={'textAlign': 'center'}
        ),
        dcc.Slider(
            min=0, 
            max=5, 
            step=.5, 
            value=0, 
            id='state_slider-3'
        ),
        # Local annotation
        html.P(
            'Adjust MSA Annotation', 
            style={
                'textAlign':'center',
                'color': '#d95f02',
                'font-weight':'bolder', 
                'margin-bottom': '0px'
            }
        ),
        dbc.RadioItems(
            id='msa_adj-3',
            options=[
                {'label':'Up', 'value':True},
                {'label':'Down', 'value':False}
            ],
            value=True,
            inline=True,
            style={'textAlign': 'center'}
        ),
        dcc.Slider(
            min=0, 
            max=5, 
            step=.5, 
            value=0, 
            id='msa_slider-3'
        )
    ])

    sidebar=html.Div(
        controls,
        style=SIDEBAR_STYLE
    )

    content=html.Div(
        [
            html.Br(),
            dcc.Graph(id='graph-3'),
            html.P('Source: Bureau of Economic Analysis'),
            html.Div(id="table-3")
        ],
        style=CONTENT_STYLE
    )

    tab3_layout=html.Div(
        dbc.Row([
            dbc.Col(sidebar, md=1), 
            dbc.Col(content, md=3)
        ])
    )
    
    return tab3_layout