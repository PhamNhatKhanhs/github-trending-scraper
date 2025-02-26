import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
from db_utils import DB_PATH

app = dash.Dash(__name__)

def load_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM github_trending", conn)
    conn.close()
    df['scrape_date'] = pd.to_datetime(df['scrape_date'])
    return df

def create_language_trend_chart(df):
    lang_trend = df.groupby(['scrape_date', 'language']).size().reset_index(name='count')
    fig = px.line(lang_trend, x='scrape_date', y='count', color='language',
                  title='Programming Language Trends Over Time')
    return fig

def create_star_changes_chart(df):
    star_changes = df.groupby('language')['star_change'].mean().sort_values(ascending=False).head(10)
    fig = px.bar(x=star_changes.index, y=star_changes.values,
                 title='Average Star Changes by Language')
    return fig

def create_topic_chart(df):
    all_topics = []
    for topics_str in df['topics'].dropna():
        if topics_str:
            all_topics.extend(topics_str.split(','))
    topic_counts = pd.Series(all_topics).value_counts().head(15)
    # Convert to DataFrame for proper plotly express handling
    topic_df = pd.DataFrame({'topic': topic_counts.index, 'count': topic_counts.values})
    fig = px.bar(topic_df, x='topic', y='count',
                 title='Most Common Repository Topics')
    return fig

app.layout = html.Div([
    html.H1('GitHub Trending Analysis Dashboard'),
    
    html.Div([
        html.Button('Refresh Data', id='refresh-button', n_clicks=0),
        html.Div(id='last-update-time')
    ]),
    
    dcc.Tabs([
        dcc.Tab(label='Language Trends', children=[
            dcc.Graph(id='language-trend-chart')
        ]),
        dcc.Tab(label='Star Changes', children=[
            dcc.Graph(id='star-changes-chart')
        ]),
        dcc.Tab(label='Topics', children=[
            dcc.Graph(id='topic-chart')
        ])
    ]),
    
    dcc.Interval(
        id='interval-component',
        interval=300000,  # update every 5 minutes
        n_intervals=0
    )
])

@app.callback(
    [Output('language-trend-chart', 'figure'),
     Output('star-changes-chart', 'figure'),
     Output('topic-chart', 'figure'),
     Output('last-update-time', 'children')],
    [Input('refresh-button', 'n_clicks'),
     Input('interval-component', 'n_intervals')]
)
def update_charts(n_clicks, n_intervals):
    df = load_data()
    last_update = f'Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
    return [
        create_language_trend_chart(df),
        create_star_changes_chart(df),
        create_topic_chart(df),
        last_update
    ]

def main():
    app.run_server(debug=True)

if __name__ == '__main__':
    main()