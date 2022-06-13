import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
from tabs import tab1, tab2, tab3

import pandas as pd
import plotly.io as pio
pio.templates.default="plotly_white"

from helper_functions import calc_index, calc_CAGR, get_balanced_panel, trend_graph, bea_graph,month_graph, create_table

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
pop=get_balanced_panel(pop, datevar='Year', format='%Y')

lau=pd.read_csv('/Users/GaryLin/Dropbox/Unison/Analytics/EconApp/data/lau.csv')
#lau=get_balanced_panel(lau, datevar='Year')
lau=get_balanced_panel(lau, datevar='Date', format='%Y-%m-%d')

bea=pd.read_csv('https://raw.githubusercontent.com/garycl/EconApp/master/data/bea.csv')
bea=get_balanced_panel(bea, datevar='Year', format='%Y')

qcew=pd.read_csv('https://raw.githubusercontent.com/garycl/EconApp/master/data/qcew.csv')
qcew=get_balanced_panel(qcew, datevar='Year', format='%Y')

# App set-up
app=dash.Dash(
    __name__, 
    external_stylesheets=[dbc.themes.FLATLY],
    meta_tags=[{"name": "viewport", "content": "width=device-width"}],
    suppress_callback_exceptions=True
)
app.title="Social and Economic Trends"
server=app.server


tab_style = {
    'background-color': '#f8f9fa',
    'border-color':'#1b9e77',
    'text-transform': 'uppercase',
    'font-size': '24px',
    'font-weight': 600,
    'align-items': 'center',
    'padding':'40px'
}

tab_selected_style = {
    'border-color':'#1b9e77',
    'color':'#1b9e77',
    'text-transform': 'uppercase',
    'font-size': '24px',
    'font-weight': 2000,
    'align-items': 'center',
    'padding':'40px'
}

# Describe the layout/ UI of the app
app.layout=html.Div(
    [
        dcc.Tabs(
            id="tabs", 
            value='tab-1', 
            children=[
                dcc.Tab(label='Population', value='tab-1', style=tab_style, selected_style=tab_selected_style),
                dcc.Tab(label='Labor Market', value='tab-2', style=tab_style, selected_style=tab_selected_style),
                dcc.Tab(label='Real GDP / Income', value='tab-3', style=tab_style, selected_style=tab_selected_style)
            ]
        ),
        html.Div(id='tabs-content')
    ],
    style={'margin-left': '20%'}
)

@app.callback(
    Output('tabs-content', 'children'),
    [Input('tabs', 'value')]
)
def render_content(tab):
    if tab == 'tab-1':
        return tab1.create_layout(pop)
    elif tab == 'tab-2':
        return tab2.create_layout(lau)
    elif tab == 'tab-3':
        return tab3.create_layout(bea)


# Tab 1 callback
@app.callback(
    Output('graph-1', 'figure'),
    Output('table-1', 'children'),
    Input('msa_dropdown', 'value'),
    Input('recession', 'value'),
    Input('nation_adj-1', 'value'),
    Input('nation_slider-1', 'value'),
    Input('state_adj-1', 'value'),
    Input('state_slider-1', 'value'),
    Input('msa_adj-1', 'value'),
    Input('msa_slider-1', 'value'),
)
    
# chart
def update_tab1_graph(
    msa, recession, 
    nation_adj, nation_slider,
    state_adj, state_slider,
    msa_adj, msa_slider):
            
    if msa is None:
        raise PreventUpdate
    else:
        state_abbrev=msa.split(', ')[1].strip().split('-')[0].strip()
        state_name=abbrev_to_us_state[state_abbrev]

    data=pop.copy()
    df=data[(data.Area=='United States') | (data.Area==state_name) | (data.Area==msa)].copy()
    df=calc_index(df, 'Population')
    df=calc_CAGR(df, 'Index')
            
    x0=df.Year.min()
    fig=trend_graph(
        df, state_name, msa, 'Index', recession,
        title=f"Population Growth Index ({x0} Level=100)",
        xaxis_title="Calendar Year",
        yaxis_title="Index",
        nation_adj=nation_adj,
        nation_slider=nation_slider,
        state_adj=state_adj,
        state_slider=state_slider,
        msa_adj=msa_adj,
        msa_slider=msa_slider
    )

    table=create_table(data, state_name, msa, 'Population', 'Thousands')
    table=dash_table.DataTable(
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
    return  fig, table

# Tab2 Callback
@app.callback(
    Output('area_dropdown', 'options'),
    Input('type_dropdown', 'value')
)
def update_area(type):
    area_list = (
        lau.loc[lau.Type==type, 'Area']
            .copy()
            .sort_values().unique()
    )
    return [{'label':area, 'value':area} for area in area_list]


@app.callback(
    Output('graph-2', 'figure'),
    Output('graph-month-2', 'figure'),
    Output('table-2', 'children'),
    Input('area_dropdown', 'value'),
    Input('yvar_dropdown', 'value'),
    Input('recession', 'value'),
    Input('nation_adj-2', 'value'),
    Input('nation_slider-2', 'value'),
    Input('state_adj-2', 'value'),
    Input('state_slider-2', 'value'),
    Input('msa_adj-2', 'value'),
    Input('msa_slider-2', 'value'),
    Input('nation_apr_adj-2', 'value'),
    Input('nation_apr_slider-2', 'value'),
    Input('state_apr_adj-2', 'value'),
    Input('state_apr_slider-2', 'value'),
    Input('msa_apr_adj-2', 'value'),
    Input('msa_apr_slider-2', 'value'),
    Input('nation_m_adj-2', 'value'),
    Input('nation_m_slider-2', 'value'),
    Input('state_m_adj-2', 'value'),
    Input('state_m_slider-2', 'value'),
    Input('msa_m_adj-2', 'value'),
    Input('msa_m_slider-2', 'value'),
)

# chart
def update_tab2_graph(
    msa, yvar, recession, 
    nation_adj, nation_slider,
    state_adj, state_slider,
    msa_adj, msa_slider,
    nation_apr_adj, nation_apr_slider,
    state_apr_adj, state_apr_slider,
    msa_apr_adj, msa_apr_slider,
    nation_m_adj, nation_m_slider,
    state_m_adj, state_m_slider,
    msa_m_adj, msa_m_slider):
            
    if msa is None:
        raise PreventUpdate
    else:
        state_abbrev=msa.split(', ')[1].strip().split('-')[0].strip()
        state_name=abbrev_to_us_state[state_abbrev]

    data=lau.copy()
    df=data[(data.Area=='United States') | (data.Area==state_name) | (data.Area==msa)].copy()
    df=df[(df.Year>=2000) & (df.Year<=2021)]
    df=df[['Area', 'Date', 'Year', 'Type', yvar]]
    df=calc_index(df, yvar)
    df=calc_CAGR(df, 'Index')
            
    x0=int(df.Year.min())
    if yvar=='Unemployment Rate':
        title="Annual Average Unemployment Rate (Seasonally Adjusted)"
        yaxis_title="Percentage"
        yvarname=yvar
        table=create_table(data, state_name, msa, yvar, 'Percentage')
    else:
        title=f"{yvar} Growth Index ({x0} Level=100)"
        yaxis_title="Index"
        yvarname='Index'
        table=create_table(data, state_name, msa, yvar, 'Thousands')

    fig=trend_graph(
        df, state_name, msa, yvarname, recession,
        title=title,
        xaxis_title="Calendar Year",
        yaxis_title=yaxis_title,
        nation_adj=nation_adj,
        nation_slider=nation_slider,
        state_adj=state_adj,
        state_slider=state_slider,
        msa_adj=msa_adj,
        msa_slider=msa_slider
    )

    df_m=data[(data.Area=='United States') | (data.Area==state_name) | (data.Area==msa)].copy()
    df_m=df_m[df_m.Year>=2020]
    df_m=df_m[['Area', 'Date', 'Year', 'Type', yvar]]
    df_m=calc_index(df_m, yvar, 'Date')

    x0_year=df_m.Date.dt.year.min()
    x0_month = df_m[df_m.Date.dt.year==x0_year].Date.min().month_name()
    if yvar=='Unemployment Rate':
        title="Monthly Unemployment Rate (Seasonally Adjusted)"
        yaxis_title="Percentage"
        yvarname=yvar
    else:
        title=f"{yvar} Growth Index ({x0_month} {x0_year} Level=100)"
        yaxis_title="Index"
        yvarname='Index'
    fig2=month_graph(
        df_m, state_name, msa, yvarname, recession,
        title=title,
        xaxis_title="Date",
        yaxis_title=yaxis_title,
        nation_apr_adj=nation_apr_adj,
        nation_apr_slider=nation_apr_slider,
        state_apr_adj=state_apr_adj,
        state_apr_slider=state_apr_slider,
        msa_apr_adj=msa_apr_adj,
        msa_apr_slider=msa_apr_slider,
        nation_m_adj=nation_m_adj,
        nation_m_slider=nation_m_slider,
        state_m_adj=state_m_adj,
        state_m_slider=state_m_slider,
        msa_m_adj=msa_m_adj,
        msa_m_slider=msa_m_slider
    )

    table=dash_table.DataTable(
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
    return  fig, fig2, table

# Tab 3
@app.callback(
    Output('graph-3', 'figure'),
    Output('table-3', 'children'),
    Input('area_dropdown', 'value'),
    Input('yvar_dropdown', 'value'),
    Input('recession', 'value'),
    Input('nation_adj-3', 'value'),
    Input('nation_slider-3', 'value'),
    Input('state_adj-3', 'value'),
    Input('state_slider-3', 'value'),
    Input('msa_adj-3', 'value'),
    Input('msa_slider-3', 'value')
)

# chart
def display_tab3_chart(
    msa, yvar, recession,
    nation_adj, nation_slider,
    state_adj, state_slider,
    msa_adj, msa_slider):
        
    if msa is None:
        raise PreventUpdate
    else:
        state_abbrev=msa.split(', ')[1].strip().split('-')[0].strip()
        state_name=abbrev_to_us_state[state_abbrev]

    data=bea.copy()
    df=data[(bea.Area=='United States') | (data.Area==state_name) | (data.Area==msa)].copy()
    df=df[['Area', 'Date', 'Year', 'Type', yvar]]
    df=calc_index(df, yvar)
    df=calc_CAGR(df, 'Index')
        
    x0=df.Year.min()
    if yvar=='Real Per Capita Personal Income':
        title="Real Per Capita Personal Income (2012 Dollars)"
        yaxis_title="Thousand Dollars"
        yvarname=yvar
        table=create_table(data, state_name, msa, yvar, 'Thousands')
    elif yvar=="Real GDP (Millions)":
        title=f"Real GDP Growth Index ({x0} Level=100)"
        yaxis_title="Index"
        yvarname='Index'
        table=create_table(data, state_name, msa, yvar, 'Thousands')
    fig=bea_graph(
        df, state_name, msa, yvarname, recession,
        title=title,
        xaxis_title="Calendar Year",
        yaxis_title=yaxis_title,
        nation_adj=nation_adj,
        nation_slider=nation_slider,
        state_adj=state_adj,
        state_slider=state_slider,
        msa_adj=msa_adj,
        msa_slider=msa_slider
    )

    table=dash_table.DataTable(
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
    return  fig, table

if __name__ == '__main__':
    app.run_server(debug=True)
