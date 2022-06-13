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
        html.H5('Select Area', style={'textAlign': 'center'}),
        dcc.Dropdown(
            id='type_dropdown',
            value='MSA',
            options=[{'label':type, 'value':type} for type in ['MSA', 'NECTA']]
        ),
        dcc.Dropdown(
            id='area_dropdown',
            value='New York-Newark-Jersey City, NY-NJ-PA',
            options=[{'label':msa, 'value':msa} for msa in msa_list]
        ),
        dcc.Dropdown(
            id='yvar_dropdown',
            value='Employment',
            options=[{'label':yvar, 'value':yvar} for yvar in ['Employment', 'Labor Force', 'Unemployment Rate']]
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
        html.H5('Annual Graph Annotation Controls', style={'textAlign':'center'}),
        # US annotation
        html.P(
            'United States',
            style={
                'textAlign':'center',
                'color': '#1b9e77',
                'font-weight':'bolder', 
                'margin-bottom': '0px'
            }
        ),
        dbc.RadioItems(
            id='nation_adj-2',
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
            id='nation_slider-2'
        ),
        # State annotation
        html.P(
            'State',
            style={
                'textAlign':'center',
                'color': '#7570b3', 
                'font-weight':'bolder', 
                'margin-bottom': '0px'
            }
        ),
        dbc.RadioItems(
            id='state_adj-2',
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
            id='state_slider-2'
        ),
        # Local annotation
        html.P(
            'MSA/NECTA', 
            style={
                'textAlign':'center',
                'color': '#d95f02',
                'font-weight':'bolder', 
                'margin-bottom': '0px'
            }
        ),
        dbc.RadioItems(
            id='msa_adj-2',
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
            id='msa_slider-2'
        ),
        html.Br(),
        html.H5('Monthly Graph Annotation Controls', style={'textAlign':'center'}),
        # US annotation
        html.P(
            'United States, April 2020',
            style={
                'textAlign':'center',
                'color': '#1b9e77',
                'font-weight':'bolder', 
                'margin-bottom': '0px'
            }
        ),
        dbc.RadioItems(
            id='nation_apr_adj-2',
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
            id='nation_apr_slider-2'
        ),
        html.P(
            'United States, Latest Month',
            style={
                'textAlign':'center',
                'color': '#1b9e77',
                'font-weight':'bolder', 
                'margin-bottom': '0px'
            }
        ),
        dbc.RadioItems(
            id='nation_m_adj-2',
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
            step=0.5, 
            value=0, 
            id='nation_m_slider-2'
        ),
        # State annotation
        html.P(
            'State, April 2020',
            style={
                'textAlign':'center',
                'color': '#7570b3', 
                'font-weight':'bolder', 
                'margin-bottom': '0px'
            }
        ),
        dbc.RadioItems(
            id='state_apr_adj-2',
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
            id='state_apr_slider-2'
        ),
        html.P(
            'State, Latest Month',
            style={
                'textAlign':'center',
                'color': '#7570b3', 
                'font-weight':'bolder', 
                'margin-bottom': '0px'
            }
        ),
        dbc.RadioItems(
            id='state_m_adj-2',
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
            id='state_m_slider-2'
        ),
        # Local annotation
        html.P(
            'MSA/NECTA, April 2020', 
            style={
                'textAlign':'center',
                'color': '#d95f02',
                'font-weight':'bolder', 
                'margin-bottom': '0px'
            }
        ),
        dbc.RadioItems(
            id='msa_apr_adj-2',
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
            id='msa_apr_slider-2'
        ),
        html.P(
            'MSA/NECTA, Latest Month', 
            style={
                'textAlign':'center',
                'color': '#d95f02',
                'font-weight':'bolder', 
                'margin-bottom': '0px'
            }
        ),
        dbc.RadioItems(
            id='msa_m_adj-2',
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
            id='msa_m_slider-2'
        )
    ])

    sidebar=html.Div(
        controls,
        style=SIDEBAR_STYLE
    )

    content=html.Div(
        [
            html.Br(),
            dcc.Graph(id='graph-2'),
            html.Br(),
            dcc.Graph(id='graph-month-2'),
            html.P('Source: Bureau of Labor Statistics'),
            html.Div(id="table-2")
        ],
        style=CONTENT_STYLE
    )

    tab2_layout=html.Div(
        dbc.Row([
            dbc.Col(sidebar, md=1), 
            dbc.Col(content, md=3)
        ])
    )
    
    return tab2_layout