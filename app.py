import dash
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from dash import dcc, html, dash_table

import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
pio.templates.default="plotly_white"

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

# calc index
def calc_index(df, variable):
    
    start=df.Year.min()
    end=df.Year.max()
    t=end-start
    
    # Calculate CAGR
    area_list=df['Area'].unique()
    for area in area_list:
        area_df=df[df['Area']==area].copy()
        vbegin=area_df.loc[area_df.Year==start, variable].values[0]
        df.loc[df.Area==area, f'Index']=df.loc[df.Area==area, variable].values /vbegin * 100
        df.loc[df.Area==area, f'Index']=df.loc[df.Area==area, f'Index'].round(3)
        
    return df


# calc cagr
def calc_CAGR(df, variable):
    
    start=df.Year.min()
    end=df.Year.max()
    t=end-start
    
    # Calculate CAGR
    area_list=df['Area'].unique()
    for area in area_list:
        area_df=df[df['Area']==area].copy()
        vbegin=area_df.loc[area_df.Year==start, variable].values[0]
        vfinal=area_df.loc[area_df.Year==end, variable].values[0]
        cagr=(vfinal/vbegin)**(1/t)-1
        cagr=cagr * 100
        cagr=round(cagr, 2)
        df.loc[df.Area==area, 'CAGR']=cagr
        
    return df

# balanced panle
def get_balanced_panel(df, datevar='Date'):
    start=df.Date.min()
    end=df.Date.max()
    for area in df.Type.unique():
        area_start=df[df.Type==area].Date.min()
        if area_start>start:
                start=area_start
        area_end=df[df.Type==area].Date.max()
        if area_end<end:
            end=area_end
    
    df=df[(df.Date>=start) & (df.Date<=end)]
    print(f'Time panel\nStart:{start}\nEnd:{end}')
    return df

# read data
pop=pd.read_csv('https://raw.githubusercontent.com/garycl/EconApp/master/data/pop.csv')
pop['Date']=pd.to_datetime(pop['Year'], format='%Y')
pop=get_balanced_panel(pop)

lau=pd.read_csv('https://raw.githubusercontent.com/garycl/EconApp/master/data/lau.csv')
#lau['Date']=pd.to_datetime(lau['Date'])
lau=lau.groupby(['Area','Type', 'Year']).mean().round(1)
lau.reset_index(inplace=True)
lau['Date']=pd.to_datetime(lau['Year'], format='%Y')
lau=lau[lau.Year>=2000]
lau['Unemployment Rate']=lau['Unemployment'].values/lau['Labor Force'].values * 100
lau['Unemployment Rate']=lau['Unemployment Rate'].round(1).astype(float)


# msa names
msa_list=lau.loc[lau.Type=='MSA', 'Area'].sort_values().unique()

def trend_graph(df, state_name, msa, yvarname, check_list, title=None,yaxis_title=None,xaxis_title=None):

    # Rename MSA
    msa_name=msa.split(',')[0].split('-')[0].strip()
    msa_name=msa_name+' MSA'
    df.loc[df.Area==msa,'Area']=msa_name 
    color_discrete_map={
        "United States": "#F77F0E",
        state_name: "#1F77B4",
        msa_name: '#2CA02E'
    }
    
    # Line Graph
    df.loc[df.Area==msa,'Area']=msa_name   
    df=df.groupby(['Area',pd.Grouper(key='Date', freq='y')]).mean().round(1)
    df.reset_index(inplace=True)
    line_graph=px.line(
        data_frame=df, 
        x='Year', y=yvarname,
        color='Area',
        color_discrete_map=color_discrete_map,
        markers=True,
        width=1200,
        height=600,
    )
    fig=go.Figure(data=line_graph)

    # Retrieve latest y-values
    xvalue=df['Year'].max()
    area_list=['United States', state_name, msa_name]
    area_dict={}
    for area in area_list:
        temp=df[df.Area==area].copy()
        temp=temp[temp.Year==temp.Year.max()]
        yvalue=temp[yvarname].values[0]
        area_dict[area]=yvalue
    area_dict=pd.DataFrame(index=area_dict.keys(), data=area_dict.values(), columns=['yvalue'])
    area_dict=area_dict.sort_values(by='yvalue', ascending=False)
    if yvarname == "Unemployment Rate":
        if area_dict['yvalue'][0]-area_dict['yvalue'][1]<0.5:
            area_dict['yvalue'][0]=area_dict['yvalue'][0]+0.5
        if area_dict['yvalue'][1]-area_dict['yvalue'][2]<0.5:
            area_dict['yvalue'][2]=area_dict['yvalue'][2]-0.5
    elif yvarname == "Index":
        if area_dict['yvalue'][0]-area_dict['yvalue'][1]<4:
            area_dict['yvalue'][0] = area_dict['yvalue'][0]+4
        if area_dict['yvalue'][1]-area_dict['yvalue'][2]<5:
            area_dict['yvalue'][2] = area_dict['yvalue'][2]-5
    area_dict=area_dict.to_dict('index')

    # Label y-values
    xvalue=df['Year'].max()
    if xvalue<2021:
        xvalue=2021
    for area in area_list:
        temp=df[df.Area==area]
        temp=temp[temp.Year==temp.Year.max()]
        yvalue=temp[yvarname].values[0].round(1)
        if yvarname=="Unemployment Rate":
            yvalue=f'{yvalue}%'
        elif yvarname=="Index":
            cagr=temp['CAGR'].values[0]
            yvalue=f"{yvalue}<br>(CAGR={cagr}%)"
        else:
            yvalue
        fig.add_annotation(
            x=xvalue, 
            y=area_dict[area]['yvalue'],
            text=f"{area}, {yvalue}",
            font=dict(
                color=color_discrete_map[area],
                size=16
            ),
            xanchor='left',
            showarrow=False,
            xshift=30
        )

    # Title layout
    xmin=df.Year.min().astype(int)
    xmax=df.Year.max().astype(int)
    if xmax<2021:
        xmax=2021
    ymin=df[yvarname].min()
    ymax=df[yvarname].max()
    yheight=ymax+(ymax-ymin)/12
    fig.update_layout(
        font_family="Arial",
        xaxis_title=xaxis_title,
        yaxis_title=yaxis_title,
        title=title,
        font=dict(
            family="Arial",
            size=14,
            color="black"
        ),
        showlegend=False,
        xaxis=dict(
            tickmode='array',
            tickvals=list(range(xmin,xmax+1,1)),
            tickangle=270,
            tickfont=dict(
              size=14,
              color='black'
            ),
            showgrid=False,
        ),
        yaxis=dict(
            tick0=0,
            tickfont=dict(
                size=14,
                color='black'
            ),
            showgrid=False
        )
    )
    
    if yvarname=="Index":
        fig.update_yaxes(range=[min(ymin-10,90), yheight+5])
    else:
        fig.update_yaxes(range=[0,yheight+1])

    # Label Recessions
    for recession in check_list:
        if recession=='tech_bust':
            fig.add_shape(
                type="rect", 
                x0=2001.3, x1=2001.9, 
                y0=0, y1=yheight, 
                fillcolor='grey',
                opacity=0.25, 
                line=dict(color='grey')
            )
            fig.add_annotation(
                x=2001, y=yheight+0.25, 
                xshift=20, yshift=20, 
                text='Tech Bust<br>Recession', 
                showarrow=False,
                font=dict(size=16)
            )
        if recession=='great_recession':
            fig.add_shape(
                type="rect", 
                x0=2008, x1=2009, 
                y0=0, y1=yheight, 
                fillcolor='grey',
                opacity=0.25, 
                line=dict(color='grey')
            )
            fig.add_annotation(
                x=2008, y=yheight+0.25, 
                xshift=20, yshift=20, 
                text=f'Great<br>Recession', 
                showarrow=False,
                font=dict(size=16)
            )
        if recession=='covid_recession':
            fig.add_shape(
                type="rect", 
                x0=2020, x1=2020.4, 
                y0=0, y1=yheight, 
                fillcolor='grey',
                opacity=0.25, 
                line=dict(color='grey')
            ),
            fig.add_annotation(
                x=2019.8, y=yheight+0.25,
                xshift=20, yshift=20,
                text=f'COVID<br>Recession', 
                showarrow=False, 
                font=dict(size=16)
            )
    return fig

def create_table(df, state_name, msa, yvarname, format=None):
    msa_name=msa.split(',')[0].split('-')[0].strip()
    msa_name=msa_name+' MSA'
    geo_list=['United States', state_name, msa]
    table=pd.DataFrame()
    for geo in geo_list:
        temp=df[df.Area==geo].copy()
        temp=temp[['Year', yvarname]].groupby('Year').mean()
        if format=="Percentage":
            temp[yvarname]=temp[yvarname].values.round(1).astype(float)
            temp[yvarname]=temp[yvarname].apply(lambda x : '{:.1f}'.format(x))
        elif format=="Thousands":
            temp[yvarname]=temp[yvarname].round(0).astype(int)
            temp[yvarname]=temp[yvarname].apply(lambda x : "{:,}".format(x))
        else:
            None
        table=pd.concat([table, temp], axis=1)
    table.reset_index(inplace=True)
    table.columns=['Year', 'United States', state_name, msa_name]
    return table


app = dash.Dash(__name__,external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# the style arguments for the sidebar.
SIDEBAR_STYLE={
    'position': 'fixed',
    'top': 0,
    'left': 0,
    'bottom': 0,
    'width': '20%',
    'padding': '20px 10px',
    'background-color': '#f8f9fa'
}

# the style arguments for the main content page.
CONTENT_STYLE={
    'margin-left': '5%',
    'margin-right': '5%',
    'top': 0,
    'padding': '20px 10px'
}
TEXT_STYLE={
    'textAlign': 'center',
    'color': '#191970'
}
CARD_TEXT_STYLE={
    'textAlign': 'center',
    'color': '#0074D9'
}

controls=dbc.Col(
    [
        html.P('Select MSA', style={'textAlign': 'center'}),
        dcc.Dropdown(id='msa_dropdown',
                     value='New York-Newark-Jersey City, NY-NJ-PA',
                     options=[{'label':msa, 'value':msa} for msa in msa_list]),
        html.Br(),
        html.P('Plot Recessions', style={'textAlign': 'center'}),
        dbc.Card([dbc.Checklist(
            id='check_list',
            options=[{'label': '2001 Tech Bust', 'value': 'tech_bust'},
                     {'label': 'Great Recession', 'value': 'great_recession'},
                     {'label': '2020 COVID-19', 'value': 'covid_recession'}
            ],
                value=['tech_bust', 'great_recession', 'covid_recession'],
                #inline=True
            )])
    ]
)

sidebar=html.Div(
    [
        html.H1(children='Parameters', style=TEXT_STYLE),
        html.Hr(),
        controls
    ],
    style=SIDEBAR_STYLE
)

content=html.Div([
    dcc.Tabs(id="tabs-example-graph", value='tab-1', children=[
        dcc.Tab(label='Population', value='tab-1'),
        dcc.Tab(label='Labor Force', value='tab-2'),
        dcc.Tab(label='Employment', value='tab-3'),
        dcc.Tab(label='Unemployment Rate', value='tab-4'),
    ]),
    html.Div(id='tabs-content-example-graph')
])

app.layout=html.Div(
    dbc.Row([
        dbc.Col(sidebar, md=3), 
        dbc.Col(content, md=6)
    ])
)


@app.callback(
    Output('tabs-content-example-graph', 'children'),
    Input('tabs-example-graph', 'value'),
    Input('msa_dropdown', 'value'),
    Input('check_list', 'value')
)

# table style
def display_chart(tab, msa, check_list):
        
    if msa is None:
        raise PreventUpdate
    else:
        state_abbrev=msa.split(', ')[1].strip().split('-')[0].strip()
        state_name=abbrev_to_us_state[state_abbrev]
    yvarname=None
    max_height=None

    if tab == 'tab-1': 
        df=pop[(pop.Area=='United States') | (pop.Area==state_name) | (pop.Area==msa)].copy()
        table=create_table(pop, state_name, msa, 'Population', 'Thousands')
        df=calc_index(df, 'Population')
        df=calc_CAGR(df, 'Index')
        yvarname='Index'
        x0=df.Year.min()
        fig=trend_graph(
            df, state_name, msa, yvarname, check_list,
            title=f"Population Growth Index ({x0} Level=100)",
            xaxis_title="Calendar Year",
            yaxis_title="Index"
        )
        return html.Div([
            html.Br(),
            dcc.Graph(
                id='graph-1-tabs',
                figure=fig
            ),
            html.P('Source: Census Population and Housing'),
            dash_table.DataTable(
                id='table-1-tabs',
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
    ])
    elif tab == 'tab-2': 
        df=lau[(lau.Area=='United States') | (lau.Area==state_name) | (lau.Area==msa)].copy()
        table=create_table(lau, state_name, msa, 'Labor Force', 'Thousands')
        df=calc_index(df, 'Labor Force')
        df=calc_CAGR(df, 'Index')
        yvarname='Index'
        x0=df.Year.min()
        fig=trend_graph(
            df, state_name, msa, yvarname, check_list,
            title=f"Labor Force Growth Index ({x0} Level=100)",
            xaxis_title="Calendar Year",
            yaxis_title="Index",
        )
        return html.Div([
            html.Br(),
            dcc.Graph(
                id='graph-2-tabs',
                figure=fig
            ),
            html.P('Source: Bureau of Labor Statistics'),
            dash_table.DataTable(
                id='table-2-tabs',
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
        ])
    elif tab == 'tab-3': 
        df=lau[(lau.Area=='United States') | (lau.Area==state_name) | (lau.Area==msa)].copy()
        table=create_table(lau, state_name, msa, 'Employment', 'Thousands')
        df=calc_index(df, 'Employment')
        df=calc_CAGR(df, 'Index')
        yvarname='Index'
        x0=df.Year.min()
        fig=trend_graph(
            df, state_name, msa, yvarname, check_list,
            title=f"Employment Growth Index ({x0} Level=100)",
            xaxis_title="Calendar Year",
            yaxis_title="Index",
        )
        return html.Div([
            html.Br(),
            dcc.Graph(
                id='graph-2-tabs',
                figure=fig
            ),
            html.P('Source: Bureau of Labor Statistics'),
            dash_table.DataTable(
                id='table-2-tabs',
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
        ])

    elif tab == 'tab-4': 
        df=lau[(lau.Area=='United States') | (lau.Area==state_name) | (lau.Area==msa)].copy()
        table=create_table(lau, state_name, msa, 'Unemployment Rate', 'Percentage')
        yvarname='Unemployment Rate'
        fig=trend_graph(
            df, state_name, msa, yvarname, check_list,
            title="Annual Average Unemployment Rate (Not Seasonally Adjusted)",
            xaxis_title="Calendar Year",
            yaxis_title="Percentage",
        )
        return html.Div([
            html.Br(),
            dcc.Graph(
                id='graph-4-tabs',
                figure=fig
            ),
            html.P('Source: Bureau of Labor Statistics'),
            dash_table.DataTable(
                id='table-4-tabs',
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
        ])


if __name__ == '__main__':
    app.run_server(debug=False)
