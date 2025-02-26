import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
from db_utils import DB_PATH

app = dash.Dash(__name__)

# Custom styles
app.layout = html.Div([
    # Header with gradient background
    html.Div([
        html.H1('GitHub Trending Analysis', 
            style={
                'textAlign': 'center',
                'color': 'white',
                'fontFamily': 'Segoe UI, Helvetica, Arial, sans-serif',
                'padding': '40px 20px',
                'margin': '0',
                'fontSize': '2.8rem',
                'fontWeight': '600',
                'letterSpacing': '0.5px'
            })
    ], style={
        'background': 'linear-gradient(135deg, #2ea44f 0%, #1a7f37 100%)',
        'marginBottom': '40px',
        'borderRadius': '0 0 20px 20px',
        'boxShadow': '0 4px 6px rgba(0,0,0,0.1)'
    }),
    
    # Summary statistics panel
    html.Div([
        html.Div([
            html.H3('Summary Statistics', style={'marginBottom': '15px'}),
            html.Div(id='summary-stats', style={
                'display': 'grid',
                'gridTemplateColumns': 'repeat(4, 1fr)',
                'gap': '15px'
            })
        ], style={
            'backgroundColor': '#f6f8fa',
            'padding': '20px',
            'borderRadius': '8px',
            'marginBottom': '30px'
        })
    ]),
    html.Div([
        html.H1('GitHub Trending Analysis Dashboard', 
                style={
                    'textAlign': 'center',
                    'color': '#24292e',
                    'fontFamily': 'Segoe UI, Helvetica, Arial, sans-serif',
                    'padding': '20px',
                    'marginBottom': '20px',
                    'borderBottom': '1px solid #e1e4e8',
                    'fontSize': '2.5rem',
                    'fontWeight': '600'
                })
    ], style={
        'backgroundColor': '#f6f8fa',
        'borderRadius': '8px',
        'marginBottom': '30px',
        'boxShadow': '0 1px 3px rgba(0,0,0,0.12)'
    }),
    
    html.Div([
        html.Button(
            'Refresh Data',
            id='refresh-button',
            n_clicks=0,
            style={
                'backgroundColor': '#2ea44f',
                'color': 'white',
                'border': 'none',
                'padding': '12px 24px',
                'borderRadius': '6px',
                'cursor': 'pointer',
                'marginRight': '15px',
                'fontWeight': 'bold',
                'transition': 'background-color 0.3s ease',
                'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
            }
        ),
        html.Div(
            id='last-update-time',
            style={
                'display': 'inline-block',
                'color': '#586069',
                'fontFamily': 'Segoe UI',
                'fontSize': '0.9rem'
            }
        )
    ], style={
        'marginBottom': '30px',
        'padding': '0 20px',
        'display': 'flex',
        'alignItems': 'center'
    }),
    
    dcc.Tabs([
        dcc.Tab(
            label='Language Trends',
            children=[dcc.Graph(id='language-trend-chart')],
            style={
                'padding': '20px',
                'fontFamily': 'Segoe UI',
                'color': '#24292e'
            },
            selected_style={
                'backgroundColor': '#f6f8fa',
                'borderTop': '3px solid #2ea44f',
                'padding': '20px',
                'fontFamily': 'Segoe UI',
                'color': '#24292e',
                'fontWeight': 'bold'
            }
        ),
        dcc.Tab(
            label='Star Changes',
            children=[dcc.Graph(id='star-changes-chart')],
            style={
                'padding': '20px',
                'fontFamily': 'Segoe UI',
                'color': '#24292e'
            },
            selected_style={
                'backgroundColor': '#f6f8fa',
                'borderTop': '3px solid #2ea44f',
                'padding': '20px',
                'fontFamily': 'Segoe UI',
                'color': '#24292e',
                'fontWeight': 'bold'
            }
        ),
        dcc.Tab(
            label='Topics',
            children=[dcc.Graph(id='topic-chart')],
            style={
                'padding': '20px',
                'fontFamily': 'Segoe UI',
                'color': '#24292e'
            },
            selected_style={
                'backgroundColor': '#f6f8fa',
                'borderTop': '3px solid #2ea44f',
                'padding': '20px',
                'fontFamily': 'Segoe UI',
                'color': '#24292e',
                'fontWeight': 'bold'
            }
        )
    ], style={
        'margin': '0 20px',
        'borderRadius': '8px',
        'overflow': 'hidden',
        'border': '1px solid #e1e4e8',
        'boxShadow': '0 2px 4px rgba(0,0,0,0.05)'
    }),
    
    dcc.Interval(
        id='interval-component',
        interval=300000,  # update every 5 minutes
        n_intervals=0
    )
], style={
    'backgroundColor': '#ffffff',
    'minHeight': '100vh',
    'margin': '0',
    'padding': '30px',
    'fontFamily': 'Segoe UI'
})

def load_data():
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql("SELECT * FROM github_trending", conn)
        conn.close()
        df['scrape_date'] = pd.to_datetime(df['scrape_date'])
        
        # Clean data
        df['language'] = df['language'].fillna('Unknown')
        df['star_change'] = df['star_change'].fillna(0)
        df['contributor_count'] = df['contributor_count'].fillna(0)
        
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return pd.DataFrame()  # Return empty DataFrame on error

def create_language_trend_chart(df):
    # Get top 10 languages by total count
    top_languages = df.groupby('language').size().nlargest(10).index
    # Filter data for top languages
    df_filtered = df[df['language'].isin(top_languages)]
    lang_trend = df_filtered.groupby(['scrape_date', 'language']).size().reset_index(name='count')
    
    fig = px.line(lang_trend, x='scrape_date', y='count', color='language',
                  title='Top 10 Programming Languages Trends Over Time')
    fig.update_layout(
        template='plotly_white',
        title_x=0.5,
        title_font_size=24,
        title_font_family='Segoe UI',
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis_title='Date',
        yaxis_title='Number of Repositories',
        legend_title='Language',
        hovermode='x unified',
        font_family='Segoe UI'
    )
    return fig

def create_star_changes_chart(df):
    star_changes = df.groupby('language')['star_change'].mean().sort_values(ascending=False).head(10)
    star_df = pd.DataFrame({'language': star_changes.index, 'avg_stars': star_changes.values})
    fig = px.bar(star_df, x='language', y='avg_stars',
                 title='Average Star Changes by Language')
    fig.update_layout(
        template='plotly_white',
        title_x=0.5,
        title_font_size=24,
        title_font_family='Segoe UI',
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis_title='Programming Language',
        yaxis_title='Average Star Change',
        showlegend=False,
        bargap=0.2,
        font_family='Segoe UI'
    )
    return fig

def create_topic_chart(df):
    # Handle empty topics
    all_topics = []
    for topics_str in df['topics'].dropna():
        if topics_str and isinstance(topics_str, str):
            topics = [t.strip() for t in topics_str.split(',') if t.strip()]
            all_topics.extend(topics)
    
    if not all_topics:
        # Create an empty chart with a message if no topics
        topic_df = pd.DataFrame({'topic': ['No topics available'], 'count': [1]})
        fig = px.pie(
            topic_df,
            values='count',
            names='topic',
            title='Distribution of Repository Topics'
        )
    else:
        # Filter out empty topics and get top 15
        topic_counts = pd.Series([t for t in all_topics if t]).value_counts().head(15)
        topic_df = pd.DataFrame({'topic': topic_counts.index, 'count': topic_counts.values})
        
        # Calculate percentages for hover text
        total = topic_df['count'].sum()
        topic_df['percentage'] = (topic_df['count'] / total * 100).round(1)
        topic_df['hover_text'] = topic_df.apply(lambda x: f'{x["topic"]}: {x["count"]} ({x["percentage"]}%)', axis=1)
        
        fig = px.pie(
            topic_df,
            values='count',
            names='topic',
            title='Distribution of Repository Topics',
            hover_data=['count', 'percentage'],
            custom_data=['hover_text'],
            hole=0.3  # Add a donut hole for better visualization
        )
        
        fig.update_traces(
            textposition='inside',
            hovertemplate='%{customdata[0]}<extra></extra>'
        )
    
    fig.update_layout(
        template='plotly_white',
        title_x=0.5,
        title_font_size=24,
        title_font_family='Segoe UI',
        plot_bgcolor='white',
        paper_bgcolor='white',
        showlegend=True,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=-0.2,
            xanchor='center',
            x=0.5
        ),
        font_family='Segoe UI'
    )
    return fig

@app.callback(
    [Output('language-trend-chart', 'figure'),
     Output('star-changes-chart', 'figure'),
     Output('topic-chart', 'figure'),
     Output('last-update-time', 'children'),
     Output('summary-stats', 'children')],
    [Input('refresh-button', 'n_clicks'),
     Input('interval-component', 'n_intervals')]
)
def update_charts(n_clicks, n_intervals):
    df = load_data()
    
    # Calculate summary statistics
    total_repos = len(df)
    total_stars = df['star_change'].sum()
    avg_contributors = df['contributor_count'].mean()
    unique_languages = df['language'].nunique()
    
    summary_stats = []
    for title, value in [
        ('Total Repositories', f'{total_repos:,}'),
        ('Total Stars Gained', f'{total_stars:,}'),
        ('Avg Contributors', f'{avg_contributors:.1f}'),
        ('Unique Languages', str(unique_languages))
    ]:
        summary_stats.append(html.Div([
            html.H4(title, style={'color': '#24292e'}),
            html.P(value, style={
                'fontSize': '24px',
                'fontWeight': 'bold',
                'color': '#24292e',
                'margin': '10px 0'
            })
        ], style={
            'textAlign': 'center',
            'padding': '20px',
            'backgroundColor': '#ffffff',
            'borderRadius': '8px',
            'boxShadow': '0 4px 6px rgba(0,0,0,0.1)',
            'transition': 'transform 0.2s ease',
            ':hover': {
                'transform': 'translateY(-5px)'
            }
        }))
    
    last_update = f'Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
    
    # Create charts with consistent styling
    fig_lang = create_language_trend_chart(df)
    fig_stars = create_star_changes_chart(df)
    fig_topics = create_topic_chart(df)
    
    return [
        fig_lang,
        fig_stars,
        fig_topics,
        last_update,
        summary_stats
    ]

def main():
    app.run_server(debug=True)

if __name__ == '__main__':
    main()