import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import requests
import pandas as pd
import sqlite3


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SOLAR])

def generate_table(dataframe, max_rows=5):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))
        ])
    ])

#Goal Leaders
with sqlite3.connect('mlsdb.sqlite') as conn:
    query = conn.execute("""
    SELECT
    p.name Name,
    p.squad Squad,
    ps.gls Goals
    FROM playerShooting ps
    INNER JOIN players p
    	ON ps.player_id = p.id
    ORDER BY goals DESC;""")
    cols = [column[0] for column in query.description]
    goalLeaders= pd.DataFrame.from_records(data = query.fetchall(), columns = cols)


goalFig = px.bar(goalLeaders.sort_values('Goals', ascending = False).head(5), x='Name', y="Goals", color = 'Squad', template = 'plotly_dark', title = 'Top Goal Scorers')
goalFig.update_layout(title_x=0.5)
#Assist Leaders
with sqlite3.connect('mlsdb.sqlite') as conn:
    query = conn.execute("""
    SELECT
    p.name Name,
    p.squad Squad,
    pp.ast Assists
    FROM playerPassing pp
    INNER JOIN players p
    	ON pp.player_id = p.id
    ORDER BY Assists DESC;""")
    cols = [column[0] for column in query.description]
    astLeaders= pd.DataFrame.from_records(data = query.fetchall(), columns = cols)

astFig = px.bar(astLeaders.sort_values('Assists', ascending = False).head(5), x='Name', y="Assists", color = 'Squad', template = 'plotly_dark', title = 'Top Assist Earners')
astFig.update_layout(title_x=0.5)
#Shot Creating Passes
with sqlite3.connect('mlsdb.sqlite') as conn:
    query = conn.execute("""
    SELECT
    p.name Name,
    p.squad Squad,
    pg.scPassLive + pg.scPassDead "Shot Creating Passes"
    FROM playerGsc pg
    INNER JOIN players p
    	ON pg.player_id = p.id
    ORDER BY "Shot Creating Passes" DESC;""")
    cols = [column[0] for column in query.description]
    scLeaders= pd.DataFrame.from_records(data = query.fetchall(), columns = cols)

scpFig = px.bar(scLeaders.sort_values('Shot Creating Passes', ascending = False).head(5), x='Name', y="Shot Creating Passes", color = 'Squad', template = 'plotly_dark', title = 'Most Shot Creating Passes')
scpFig.update_layout(title_x=0.5)
#Tackles Won
with sqlite3.connect('mlsdb.sqlite') as conn:
    query = conn.execute("""
    SELECT
    p.name Name,
    p.squad Squad,
    d.tklW "Won Tackles"
    FROM playerDefense d
    INNER JOIN players p
    	ON d.player_id = p.id
    ORDER BY "Won Tackles" DESC;""")
    cols = [column[0] for column in query.description]
    tklWLeaders= pd.DataFrame.from_records(data = query.fetchall(), columns = cols)

tklWFig = px.bar(tklWLeaders.sort_values('Won Tackles', ascending = False).head(5), x='Name', y="Won Tackles", color = 'Squad', template = 'plotly_dark', title = 'Most Successful Tackles')
tklWFig.update_layout(title_x=0.5)

#Tackle Percentage where at least 50 tackles were attempted
with sqlite3.connect('mlsdb.sqlite') as conn:
    query = conn.execute("""
    SELECT
    p.name Name,
    p.squad Squad,
    ROUND(CAST(d.tklW AS REAL)/ (d.tklAttThird + d.tklDefThird + d.tklMidThird), 2) "Tackle Percentage"
    FROM playerDefense d
    INNER JOIN players p
    	ON d.player_id = p.id
    WHERE (d.tklAttThird + d.tklDefThird + d.tklMidThird) > 25
    ORDER BY "Tackle Percentage" DESC;""")
    cols = [column[0] for column in query.description]
    tklPercentLeaders= pd.DataFrame.from_records(data = query.fetchall(), columns = cols)

tklPFig = px.bar(tklPercentLeaders.sort_values('Tackle Percentage', ascending = False).head(5), x='Name', y="Tackle Percentage", color = 'Squad', template = 'plotly_dark', title = 'Highest Successful Tackle Percantage')
tklPFig.update_layout(title_x=0.5)
#Highest Save Percentage among keepers with at least 10 games
with sqlite3.connect('mlsdb.sqlite') as conn:
    query = conn.execute("""
    SELECT
    p.name Name,
    p.squad Squad,
    ROUND(CAST(k.saves AS float)/CAST(k.sota AS float), 2) "Save Percentage"
    FROM playerKeepers k
    INNER JOIN players p
    	ON k.player_id = p.id
    WHERE k.starts > 10
    ORDER BY "Save Percentage" DESC;""")
    cols = [column[0] for column in query.description]
    savePercentLeaders= pd.DataFrame.from_records(data = query.fetchall(), columns = cols)

savePFig = px.bar(savePercentLeaders.sort_values('Save Percentage', ascending = False,).head(5), x='Name', y='Save Percentage', color = 'Squad', template = 'plotly_dark', title = 'Highest Save Percentage')
savePFig.update_layout(title_x=0.5)

app.layout = html.Div(children=[
    html.H1('MLS Dashboard',
             style={'textAlign': 'center', 'color': 'white','font-size': 40, 'margin-bottom':'2em'}),
    html.H2('League Leaders',
             style={'textAlign': 'center', 'color': 'white','font-size': 30}),

    dbc.Row(
        [
            dbc.Col(html.Div([
                html.H4('Top Goal Scorers',
                    style={'textAlign': 'center', 'color': 'white', 'margin-bottom':'1em', 'margin-top':'1em'}),
                dcc.Graph(
                    id='goal-graph',
                    figure=goalFig,
                )], id='plot1'),
            lg={'size':6, 'offset':0}, md={'size':8, 'offset':2}),
            dbc.Col(html.Div([
                html.H4('Most Assists',
                    style={'textAlign': 'center', 'color': 'white', 'margin-bottom':'1em', 'margin-top':'1em'}),
                dcc.Graph(
                    id='ast-graph',
                    figure=astFig,
                )], id='plot2'),
            lg={'size':6, 'offset':0}, md={'size':8, 'offset':2}),
        ]
    ),

    dbc.Row(
        [
            dbc.Col(html.Div([
                html.H4('Most Shot Creating Passes',
                    style={'textAlign': 'center', 'color': 'white', 'margin-bottom':'1em', 'margin-top':'1em'}),
                dcc.Graph(
                    id='scp-graph',
                    figure=scpFig,
                )], id='plot3'),
            lg={'size':6, 'offset':0}, md={'size':8, 'offset':2}),
            dbc.Col(html.Div([
                html.H4('Most Successful Tackles',
                    style={'textAlign': 'center', 'color': 'white', 'margin-bottom':'1em', 'margin-top':'1em'}),
                dcc.Graph(
                    id='tklw-graph',
                    figure=tklWFig,
                )], id='plot4'),
            lg={'size':6, 'offset':0}, md={'size':8, 'offset':2}),
        ]
    ),

    dbc.Row(
        [
            dbc.Col(html.Div([
                html.H4('Highest Tackle Percent (Minimum 25 tackles)',
                    style={'textAlign': 'center', 'color': 'white', 'margin-bottom':'1em', 'margin-top':'1em'}),
                dcc.Graph(
                    id='tklp-graph',
                    figure=tklPFig,
                )], id='plot5'),
            lg={'size':6, 'offset':0}, md={'size':8, 'offset':2}),
            dbc.Col(html.Div([
                html.H4('Highest Save Percent (Minimum 10 starts)',
                    style={'textAlign': 'center', 'color': 'white', 'margin-bottom':'1em', 'margin-top':'1em'}),
                dcc.Graph(
                    id='savep-graph',
                    figure=savePFig,
                )], id='plot6'),
            lg={'size':6, 'offset':0}, md={'size':8, 'offset':2}),
        ]
    ),
])

if __name__ == '__main__':
    app.run_server(debug=True)
