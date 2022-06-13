import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Calculate Index
def calc_index(df, variable, timevar='Year'):
    
    start=df[timevar].min()
    
    # Calculate Index
    area_list=df['Area'].unique()
    for area in area_list:
        area_df=df[df['Area']==area].copy()
        vbegin=area_df.loc[area_df[timevar]==start, variable].values[0]
        df.loc[df.Area==area, f'Index']=df.loc[df.Area==area, variable].values /vbegin * 100
        df.loc[df.Area==area, f'Index']=df.loc[df.Area==area, f'Index'].round(3)
        
    return df

# Calculate CAGR
def calc_CAGR(df, variable):
    
    start=df['Year'].min()
    end=df['Year'].max()
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

# Balanced panel
def get_balanced_panel(df, datevar, format):
    df['Date']=pd.to_datetime(df[datevar], format=format)
    df['Year']=df['Date'].dt.year
    start=df[datevar].min()
    end=df[datevar].max()
    for area in df.Type.unique():
        area_start=df[df.Type==area][datevar].min()
        if area_start>start:
                start=area_start
        area_end=df[df.Type==area][datevar].max()
        if area_end<end:
            end=area_end
    
    df=df[(df[datevar]>=start) & (df[datevar]<=end)]
    df=df[df.Year>=2000]
    print(f'Time panel\nStart:{start}\nEnd:{end}')
    return df

# Graph
def trend_graph(
    df, state_name, msa, yvarname, recession, 
    title=None, yaxis_title=None, xaxis_title=None, 
    nation_adj=True, state_adj=True, msa_adj=True,
    nation_slider=0, state_slider=0, msa_slider=0):

    # Rename MSA
    msa_name=msa.split(',')[0].split('-')[0].strip()
    type = df.loc[df.Area==msa,'Type'].values[0]
    msa_name=f'{msa_name} {type}'
    df.loc[df.Area==msa,'Area']=msa_name 
    symbols = ['circle', 'triangle-up', 'square']
    color_discrete_map={
        "United States": "#1b9e77",
        state_name: "#7570b3",
        msa_name: '#d95f02'
    }
    
    # Line Graph
    df.loc[df.Area==msa,'Area']=msa_name
    df['Size']=1   
    df=df.groupby(['Area',pd.Grouper(key='Date', freq='y')]).mean().round(1)
    df.reset_index(inplace=True)
    graph=px.scatter(
        data_frame=df, 
        x='Year', y=yvarname,
        color='Area',
        color_discrete_map=color_discrete_map,
        symbol= df['Area'],
        size=df['Size'],
        size_max=7,
        symbol_sequence=symbols,
        width=1200,
        height=600,
        hover_data={'Area':True, yvarname:True, 'Size':False}
    ).update_traces(mode="lines+markers", line=dict(width=3))
    fig=go.Figure(data=graph)

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
        title_font_family="Arial",
        xaxis_title=xaxis_title,
        yaxis_title=yaxis_title,
        title=title,
        font=dict(
            size=18,
            color="black"
        ),
        showlegend=False,
        xaxis=dict(
            tickmode='array',
            tickvals=list(range(xmin,xmax+1,1)),
            tickangle=270,
            tickfont=dict(
              size=18,
              color='black'
            ),
            showgrid=False,
        ),
        yaxis=dict(
            tick0=0,
            tickfont=dict(
                size=18,
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
    if recession:
        if xmin<=2001 and xmax>=2002:
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
                font=dict(size=18)
            )
        if xmin<=2008 and xmax>=2009:
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
                font=dict(size=18)
            )
        if xmin<=2020 and xmax>=2021:
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
                font=dict(size=18)
            )

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
        gap = 4.5
        if area_dict['yvalue'][0]-area_dict['yvalue'][1]<gap:
            diff = (area_dict['yvalue'][0]-area_dict['yvalue'][1])
            area_dict['yvalue'][0]=area_dict['yvalue'][0]+(gap-diff)

        if area_dict['yvalue'][1]-area_dict['yvalue'][2]<gap:
            diff = area_dict['yvalue'][1]-area_dict['yvalue'][2]
            area_dict['yvalue'][2]=area_dict['yvalue'][2]-(gap-diff)
        if area_dict['yvalue'][0]>ymax:
            diff=area_dict['yvalue'][0]-ymax
            for i in [0,1,2]:
                area_dict['yvalue'][i]=area_dict['yvalue'][i]-diff
    area_dict=area_dict.to_dict('index')

    # Label y-values
    if nation_adj:
        new_nation_slider=nation_slider
    else:
        new_nation_slider=nation_slider * (-1)
    if state_adj:
        new_state_slider=state_slider
    else:
        new_state_slider=state_slider * (-1)
    if msa_adj:
        new_msa_slider=msa_slider
    else:
        new_msa_slider=msa_slider * (-1)

    adjustment_dict = {
        'United States':new_nation_slider,
        state_name:new_state_slider,
        msa_name:new_msa_slider
    }
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
            yvalue=f"<br>{yvalue} (CAGR={cagr}%)"
        else:
            yvalue
        fig.add_annotation(
            x=xvalue, 
            y=area_dict[area]['yvalue']+(adjustment_dict[area]),
            text=f"<b>{area}, {yvalue}</b>",
            font=dict(
                color=color_discrete_map[area],
                size=18,
            ),
            align="left",
            xanchor='left',
            showarrow=False,
            xshift=15
        )
    return fig

# Create table
def create_table(df, state_name, msa, yvarname, format=None):
    msa_name=msa.split(',')[0].split('-')[0].strip()
    type = df.loc[df.Area==msa,'Type'].values[0]
    msa_name=f'{msa_name} {type}'
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


# Graph
def bea_graph(
    data, state_name, msa, yvarname, recession, 
    title=None, yaxis_title=None, xaxis_title=None,
    nation_adj=True, state_adj=True, msa_adj=True,
    nation_slider=0, state_slider=0, msa_slider=0):

    df = data.copy()
    # Rename MSA
    msa_name=msa.split(',')[0].split('-')[0].strip()
    type = df.loc[df.Area==msa,'Type'].values[0]
    msa_name=f'{msa_name} {type}'
    df.loc[df.Area==msa,'Area']=msa_name 
    symbols = ['circle', 'triangle-up', 'square']
    color_discrete_map={
        "United States": "#1b9e77",
        state_name: "#7570b3",
        msa_name: '#d95f02'
    }
    
    if yvarname=="Real Per Capita Personal Income":
        df[yvarname]=df[yvarname].apply(lambda x:x/10**3)
    # Line Graph
    df.loc[df.Area==msa,'Area']=msa_name
    df['Size']=1   
    df=df.groupby(['Area',pd.Grouper(key='Date', freq='y')]).mean().round(1)
    df.reset_index(inplace=True)
    graph=px.scatter(
        data_frame=df, 
        x='Year', y=yvarname,
        color='Area',
        color_discrete_map=color_discrete_map,
        symbol= df['Area'],
        size=df['Size'],
        size_max=7,
        symbol_sequence=symbols,
        width=1200,
        height=600,
        hover_data={'Area':True, yvarname:True, 'Size':False}
    ).update_traces(mode="lines+markers", line=dict(width=3))
    fig=go.Figure(data=graph)

    # Title layout
    xmin=df.Year.min().astype(int)
    xmax=df.Year.max().astype(int)
    if xmax<2021:
        xmax=2021
    ymin=df[yvarname].min()
    ymax=df[yvarname].max()
    yheight=ymax+(ymax-ymin)/12
    if yvarname=="Real Per Capita Personal Income":
        yheight=yheight+5

    fig.update_layout(
        font_family="Arial",
        title_font_family="Arial",
        xaxis_title=xaxis_title,
        yaxis_title=yaxis_title,
        title=title,
        font=dict(
            size=18,
            color="black"
        ),
        showlegend=False,
        xaxis=dict(
            tickmode='array',
            tickvals=list(range(xmin,xmax+1,1)),
            tickangle=270,
            tickfont=dict(
              size=18,
              color='black'
            ),
            showgrid=False,
        ),
        yaxis=dict(
            tick0=0,
            tickfont=dict(
                size=18,
                color='black'
            ),
            showgrid=False
        )
    )
    
    if yvarname=="Index":
        fig.update_yaxes(range=[min(ymin-10,90), yheight+5])
    else:
        fig.update_yaxes(range=[0,yheight+5])

    # Label Recessions
    if recession:
        if xmin<=2001 and xmax>=2002:
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
                font=dict(size=18)
            )
        if xmin<=2008 and xmax>=2009:
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
                font=dict(size=18)
            )
        if xmin<=2020 and xmax>=2021:
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
                font=dict(size=18)
            )

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

    gap = 8
    if yvarname=="Real Per Capita Personal Income":
        gap = 5
    if area_dict['yvalue'][0]-area_dict['yvalue'][1]<gap:
        diff = (area_dict['yvalue'][0]-area_dict['yvalue'][1])
        area_dict['yvalue'][0]=area_dict['yvalue'][0]+(gap-diff)*1.2

    if area_dict['yvalue'][1]-area_dict['yvalue'][2]<gap:
        diff = area_dict['yvalue'][1]-area_dict['yvalue'][2]
        area_dict['yvalue'][2]=area_dict['yvalue'][2]-(gap-diff)*1.2

    if area_dict['yvalue'][0]>ymax:
        diff=area_dict['yvalue'][0]-ymax
        for i in [0,1,2]:
            area_dict['yvalue'][i]=area_dict['yvalue'][i]-diff
    area_dict=area_dict.to_dict('index')

    # Label y-values
    if nation_adj:
        new_nation_slider=nation_slider
    else:
        new_nation_slider=nation_slider * (-1)
    if state_adj:
        new_state_slider=state_slider
    else:
        new_state_slider=state_slider * (-1)
    if msa_adj:
        new_msa_slider=msa_slider
    else:
        new_msa_slider=msa_slider * (-1)

    adjustment_dict = {
        'United States':new_nation_slider,
        state_name:new_state_slider,
        msa_name:new_msa_slider
    }
    xvalue=df['Year'].max()
    if xvalue<2021:
        xvalue=2020
    for area in area_list:
        temp=df[df.Area==area].copy()
        temp=temp[temp.Year==temp.Year.max()]
        yvalue=temp[yvarname].values[0].round(1)
        if yvarname=="Real Per Capita Personal Income":
            yvalue=f'{yvalue}'
        elif yvarname=="Index":
            cagr=temp['CAGR'].values[0]
            yvalue=f"<br>{yvalue} (CAGR={cagr}%)"
        fig.add_annotation(
            x=xvalue, 
            y=area_dict[area]['yvalue']+(adjustment_dict[area]),
            text=f"<b>{area}, {yvalue}</b>",
            font=dict(
                color=color_discrete_map[area],
                size=18,
            ),
            align="left",
            xanchor='left',
            showarrow=False,
            xshift=25
        )
    return fig


def month_graph(
    df, state_name, msa, yvarname, recession, 
    title=None, yaxis_title=None, xaxis_title=None,
    nation_apr_adj=True, state_apr_adj=True, msa_apr_adj=True,
    nation_apr_slider=0, state_apr_slider=0, msa_apr_slider=0,
    nation_m_adj=True, state_m_adj=True, msa_m_adj=True,
    nation_m_slider=0, state_m_slider=0, msa_m_slider=0):

    # Rename MSA
    msa_name=msa.split(',')[0].split('-')[0].strip()
    type = df.loc[df.Area==msa,'Type'].values[0]
    msa_name=f'{msa_name} {type}'
    df.loc[df.Area==msa,'Area']=msa_name 
    symbols = ['square', 'circle', 'triangle-up']
    color_discrete_map={
        "United States": "#1b9e77",
        state_name: "#7570b3",
        msa_name: '#d95f02'
    }

    # Line Graph
    df.loc[df.Area==msa,'Area']=msa_name
    df['Size']=1   
    graph=px.scatter(
        data_frame=df, 
        x='Date', y=yvarname,
        color='Area',
        color_discrete_map=color_discrete_map,
        symbol= df['Area'],
        size=df['Size'],
        size_max=7,
        symbol_sequence=symbols,
        width=1200,
        height=600,
        hover_data={'Area':True, yvarname:True, 'Size':False}
    ).update_traces(mode="lines+markers", line=dict(width=3))
    fig=go.Figure(data=graph)


    # Title layout
    ymin=df[yvarname].min()
    ymax=df[yvarname].max()
    yheight=ymax+(ymax-ymin)/12
    if yvarname=="Real Per Capita Personal Income":
        yheight=yheight+5

    fig.update_layout(
        font_family="Arial",
        title_font_family="Arial",
        xaxis_title=xaxis_title,
        yaxis_title=yaxis_title,
        title=title,
        font=dict(
            size=18,
            color="black"
        ),
        showlegend=False,
        xaxis=dict(
            tickfont=dict(
              size=18,
              color='black'
            ),
            showgrid=False,
        ),
        yaxis=dict(
            tick0=0,
            tickfont=dict(
                size=18,
                color='black'
            ),
            showgrid=False
        )
    )

    if yvarname=="Index":
        fig.update_yaxes(range=[min(ymin-10,90), yheight+5])
    else:
        fig.update_yaxes(range=[0,yheight+5])

    if recession:
        fig.add_shape(
            type="rect", 
            x0=pd.to_datetime('2020-02-01'), 
            x1=pd.to_datetime('2020-04-01'), 
            y0=0, y1=yheight, 
            fillcolor='grey',
            opacity=0.25, 
            line=dict(color='grey')
        ),
        fig.add_annotation(
            x=pd.to_datetime('2020-02-15'), 
            y=yheight+0.5,
            xshift=20, yshift=25,
            text=f'COVID<br>Recession', 
            showarrow=False, 
            font=dict(size=18)
        )

    # Label April 2020 y-values
    area_list=['United States', state_name, msa_name]
    area_dict={}
    for area in area_list:
        temp=df[df.Area==area].copy()
        temp=temp[temp.Date=='2020-04-01']
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
        gap = 2
        if area_dict['yvalue'][0]-area_dict['yvalue'][1]<gap:
            diff = (area_dict['yvalue'][0]-area_dict['yvalue'][1])
            area_dict['yvalue'][0]=area_dict['yvalue'][0]+(gap-diff)

        if area_dict['yvalue'][1]-area_dict['yvalue'][2]<gap:
            diff = area_dict['yvalue'][1]-area_dict['yvalue'][2]
            area_dict['yvalue'][2]=area_dict['yvalue'][2]-(gap-diff)
        if area_dict['yvalue'][0]>ymin:
            diff=area_dict['yvalue'][0]-ymin
            for i in [0,1,2]:
                area_dict['yvalue'][i]=area_dict['yvalue'][i]-diff
    area_dict=area_dict.to_dict('index')


    # Label y-values
    if nation_apr_adj:
        new_nation_slider=nation_apr_slider
    else:
        new_nation_slider=nation_apr_slider * (-1)
    if state_apr_adj:
        new_state_slider=state_apr_slider
    else:
        new_state_slider=state_apr_slider * (-1)
    if msa_apr_adj:
        new_msa_slider=msa_apr_slider
    else:
        new_msa_slider=msa_apr_slider * (-1)

    adjustment_dict = {
        'United States':new_nation_slider,
        state_name:new_state_slider,
        msa_name:new_msa_slider
    }
    xvalue='2020-04-01'
    year=df[df.Date==xvalue].Date.dt.year.values[0]
    month_abbrev = df[df.Date==xvalue].Date.dt.month_name().values[0]
    month_abbrev = month_abbrev[0:3]
    for area in area_list:
        temp=df[df.Area==area].copy()
        temp=temp[temp.Date=='2020-04-01']
        yvalue=temp[yvarname].values[0].round(1)
        yvalue=f"({month_abbrev} {year}), {yvalue}"
        fig.add_annotation(
            x=pd.to_datetime('2020-06-01'), 
            y=area_dict[area]['yvalue']+adjustment_dict[area],
            text=f"<b>{area} {yvalue}</b>",
            font=dict(
                color=color_discrete_map[area],
                size=18,
            ),
            align="left",
            xanchor='left',
            showarrow=False,
            xshift=25
        )

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
        gap = 4.5
        if area_dict['yvalue'][0]-area_dict['yvalue'][1]<gap:
            diff = (area_dict['yvalue'][0]-area_dict['yvalue'][1])
            area_dict['yvalue'][0]=area_dict['yvalue'][0]+(gap-diff)

        if area_dict['yvalue'][1]-area_dict['yvalue'][2]<gap:
            diff = area_dict['yvalue'][1]-area_dict['yvalue'][2]
            area_dict['yvalue'][2]=area_dict['yvalue'][2]-(gap-diff)
        if area_dict['yvalue'][0]>ymax:
            diff=area_dict['yvalue'][0]-ymax
            for i in [0,1,2]:
                area_dict['yvalue'][i]=area_dict['yvalue'][i]-diff
    area_dict=area_dict.to_dict('index')


    # Label y-values
    if nation_m_adj:
        new_nation_slider=nation_m_slider
    else:
        new_nation_slider=nation_m_slider * (-1)
    if state_m_adj:
        new_state_slider=state_m_slider
    else:
        new_state_slider=state_m_slider * (-1)
    if msa_m_adj:
        new_msa_slider=msa_m_slider
    else:
        new_msa_slider=msa_m_slider * (-1)

    adjustment_dict = {
        'United States':new_nation_slider,
        state_name:new_state_slider,
        msa_name:new_msa_slider
    }
    xvalue=df.Date.max()
    year=df[df.Date==xvalue].Date.dt.year.values[0]
    month_abbrev = df[df.Date==xvalue].Date.dt.month_name().values[0]
    month_abbrev = month_abbrev[0:3]
    for area in area_list:
        temp=df[df.Area==area].copy()
        temp=temp[temp.Date==temp.Date.max()]
        yvalue=temp[yvarname].values[0].round(1)
        yvalue=f"<br>({month_abbrev} {year}), {yvalue}"
        fig.add_annotation(
            x=xvalue, 
            y=area_dict[area]['yvalue']+adjustment_dict[area],
            text=f"<b>{area} {yvalue}</b>",
            font=dict(
                color=color_discrete_map[area],
                size=18,
            ),
            align="left",
            xanchor='left',
            showarrow=False,
            xshift=25
        )
    return fig