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


goalFig = px.bar(goalLeaders.sort_values('Goals', ascending = False).head(20), x='Name', y="Goals", color = 'Squad', template = 'plotly', title = 'Top Goal Scorers')
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
#Tackle Percentage where at least 50 tackles were attempted
with sqlite3.connect('mlsdb.sqlite') as conn:
    query = conn.execute("""
    SELECT
    p.name Name,
    p.squad Squad,
    ROUND(d.tklW/ (d.tklAttThird + d.tklDefThird + d.tklMidThird), 2) "Tackle Percentage"
    FROM playerDefense d
    INNER JOIN players p
    	ON d.player_id = p.id
    WHERE (d.tklAttThird + d.tklDefThird + d.tklMidThird) > 25
    ORDER BY "Tackle Percentage" DESC;""")
    cols = [column[0] for column in query.description]
    tklPercentLeaders= pd.DataFrame.from_records(data = query.fetchall(), columns = cols)
#Interceptions
with sqlite3.connect('mlsdb.sqlite') as conn:
    query = conn.execute("""
    SELECT
    p.name Name,
    p.squad Squad,
    d.int Interceptions
    FROM playerDefense d
    INNER JOIN players p
    	ON d.player_id = p.id
    ORDER BY Interceptions DESC;""")
    cols = [column[0] for column in query.description]
    tklPercentLeaders= pd.DataFrame.from_records(data = query.fetchall(), columns = cols)
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


app.layout = html.Div(children=[
    html.H1(children='MLS Dashboard'),
    html.H2(children='League Leaders'),

    html.H4(children='Top Goal Scorers'),
    generate_table(goalLeaders),

    dcc.Graph(
        id='example-graph',
        figure=goalFig
    ),

    html.H4(children='Most Assists'),
    generate_table(astLeaders),

    html.H4(children='Most Shot Creating Passes'),
    generate_table(scLeaders),

    html.H4(children='Most Tackles Won'),
    generate_table(tklWLeaders),

    html.H4(children='Highest Tackle Percent (Minimum 25 tackles)'),
    generate_table(tklPercentLeaders),

    html.H4(children='Highest Save Percent (Minimum 10 starts)'),
    generate_table(savePercentLeaders)
])

if __name__ == '__main__':
    app.run_server(debug=True)
