# scripts/dashboard.py
# Mô-đun tạo bảng điều khiển web để hiển thị phân tích GitHub Trending
# Sử dụng Dash framework để tạo giao diện người dùng tương tác

import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
from db_utils import DB_PATH

# Khởi tạo ứng dụng Dash
app = dash.Dash(__name__)

# Thiết lập giao diện người dùng với các thành phần tùy chỉnh
# Sử dụng CSS Grid và Flexbox để tạo layout linh hoạt
app.layout = html.Div([
    # Header with gradient background
    html.Div([
        html.H1('GitHub Trending Analysis', 
            style={
                'textAlign': 'center',
                'color': 'white',
                'fontFamily': '"Segoe UI", system-ui, -apple-system, sans-serif',
                'padding': '40px 20px',
                'margin': '0',
                'fontSize': '2.8rem',
                'fontWeight': '600',
                'letterSpacing': '0.5px',
                'textShadow': '0 2px 4px rgba(0,0,0,0.1)'
            })
    ], style={
        'background': 'linear-gradient(135deg, #2ea44f 0%, #1a7f37 100%)',
        'marginBottom': '40px',
        'borderRadius': '0 0 30px 30px',
        'boxShadow': '0 4px 15px rgba(0,0,0,0.1)'
    }),
    
    # Summary statistics panel with improved grid layout
    html.Div([
        html.Div([
            html.H3('Summary Statistics', 
                style={
                    'marginBottom': '20px',
                    'color': '#24292e',
                    'fontSize': '1.8rem',
                    'fontWeight': '600',
                    'textAlign': 'center'
                }),
            html.Div(id='summary-stats', style={
                'display': 'grid',
                'gridTemplateColumns': 'repeat(auto-fit, minmax(250px, 1fr))',
                'gap': '20px',
                'padding': '10px'
            })
        ], style={
            'backgroundColor': '#ffffff',
            'padding': '30px',
            'borderRadius': '16px',
            'boxShadow': '0 4px 12px rgba(0,0,0,0.05)',
            'marginBottom': '40px',
            'border': '1px solid #e1e4e8'
        })
    ]),
    
    # Refresh button and last update time with improved styling
    html.Div([
        html.Button(
            'Refresh Data',
            id='refresh-button',
            n_clicks=0,
            style={
                'backgroundColor': '#2ea44f',
                'color': 'white',
                'border': 'none',
                'padding': '12px 28px',
                'borderRadius': '8px',
                'cursor': 'pointer',
                'marginRight': '20px',
                'fontWeight': '600',
                'fontSize': '1rem',
                'transition': 'all 0.3s ease',
                'boxShadow': '0 2px 8px rgba(46,164,79,0.2)',
                'hover': {
                    'backgroundColor': '#2c974b',
                    'transform': 'translateY(-1px)',
                    'boxShadow': '0 4px 12px rgba(46,164,79,0.3)'
                }
            }
        ),
        html.Div(
            id='last-update-time',
            style={
                'display': 'inline-block',
                'color': '#586069',
                'fontFamily': '"Segoe UI", system-ui, -apple-system, sans-serif',
                'fontSize': '0.95rem'
            }
        )
    ], style={
        'marginBottom': '35px',
        'padding': '0 20px',
        'display': 'flex',
        'alignItems': 'center'
    }),
    
    # Tabs with enhanced styling
    dcc.Tabs([
        dcc.Tab(
            label='Language Trends',
            children=[dcc.Graph(id='language-trend-chart')],
            style={
                'padding': '20px',
                'fontFamily': '"Segoe UI", system-ui, -apple-system, sans-serif',
                'color': '#586069',
                'borderBottom': '2px solid transparent'
            },
            selected_style={
                'backgroundColor': '#ffffff',
                'borderTop': '3px solid #2ea44f',
                'padding': '20px',
                'fontFamily': '"Segoe UI", system-ui, -apple-system, sans-serif',
                'color': '#24292e',
                'fontWeight': '600'
            }
        ),
        dcc.Tab(
            label='Star Changes',
            children=[dcc.Graph(id='star-changes-chart')],
            style={
                'padding': '20px',
                'fontFamily': '"Segoe UI", system-ui, -apple-system, sans-serif',
                'color': '#586069',
                'borderBottom': '2px solid transparent'
            },
            selected_style={
                'backgroundColor': '#ffffff',
                'borderTop': '3px solid #2ea44f',
                'padding': '20px',
                'fontFamily': '"Segoe UI", system-ui, -apple-system, sans-serif',
                'color': '#24292e',
                'fontWeight': '600'
            }
        ),
        dcc.Tab(
            label='Stars vs Contributors',
            children=[dcc.Graph(id='stars-contributors-chart')],
            style={
                'padding': '20px',
                'fontFamily': '"Segoe UI", system-ui, -apple-system, sans-serif',
                'color': '#586069',
                'borderBottom': '2px solid transparent'
            },
            selected_style={
                'backgroundColor': '#ffffff',
                'borderTop': '3px solid #2ea44f',
                'padding': '20px',
                'fontFamily': '"Segoe UI", system-ui, -apple-system, sans-serif',
                'color': '#24292e',
                'fontWeight': '600'
            }
        )
    ], style={
        'margin': '0 20px 40px 20px',
        'borderRadius': '12px',
        'overflow': 'hidden',
        'border': '1px solid #e1e4e8',
        'boxShadow': '0 4px 12px rgba(0,0,0,0.05)'
    }),
    
    dcc.Interval(
        id='interval-component',
        interval=300000,  # update every 5 minutes
        n_intervals=0
    )
], style={
    'backgroundColor': '#f6f8fa',
    'minHeight': '100vh',
    'margin': '0',
    'padding': '30px',
    'fontFamily': '"Segoe UI", system-ui, -apple-system, sans-serif'
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
        
        # Ensure topics are properly handled
        df['topics'] = df['topics'].fillna('')  # Convert NaN to empty string
        df['topics'] = df['topics'].astype(str)  # Convert all values to string
        df['topics'] = df['topics'].apply(lambda x: x if x != 'nan' else '')  # Convert 'nan' string to empty string
        
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return pd.DataFrame()  # Return empty DataFrame on error

def create_language_trend_chart(df):
    top_languages = df.groupby('language').size().nlargest(10).index
    df_filtered = df[df['language'].isin(top_languages)]
    lang_trend = df_filtered.groupby(['scrape_date', 'language']).size().reset_index(name='count')
    
    fig = px.area(lang_trend, x='scrape_date', y='count', color='language',
                  title='Programming Language Trends',
                  groupnorm='percent')
    fig.update_layout(
        template='plotly_white',
        title_x=0.5,
        title_font_size=24,
        title_font_family='Segoe UI',
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis_title='Date',
        yaxis_title='Percentage',
        legend_title='Language',
        hovermode='x unified',
        font_family='Segoe UI',
        margin=dict(l=40, r=40, t=60, b=40),
        showlegend=True,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=-0.2,
            xanchor='center',
            x=0.5
        )
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

def create_stars_contributors_chart(df):
    # Create a scatter plot of stars vs contributors
    fig = px.scatter(
        df,
        x='stars',
        y='contributor_count',
        color='language',
        title='Repository Stars vs Contributors by Language',
        hover_data=['full_name', 'star_change'],
        labels={
            'stars': 'Total Stars',
            'contributor_count': 'Number of Contributors',
            'language': 'Programming Language',
            'full_name': 'Repository',
            'star_change': 'Star Change'
        },
        color_discrete_sequence=px.colors.qualitative.Set3
    )

    # Update layout for consistent styling
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
        font_family='Segoe UI',
        hovermode='closest'
    )

    # Update traces for better visualization
    fig.update_traces(
        marker=dict(size=10, opacity=0.7),
        hovertemplate='<b>%{customdata[0]}</b><br>'
                      'Stars: %{x:,}<br>'
                      'Contributors: %{y:,}<br>'
                      'Star Change: %{customdata[1]:+,}<br>'
                      'Language: %{marker.color}<extra></extra>'
    )

    return fig

@app.callback(
    [Output('language-trend-chart', 'figure'),
     Output('star-changes-chart', 'figure'),
     Output('stars-contributors-chart', 'figure'),
     Output('last-update-time', 'children'),
     Output('summary-stats', 'children')],
    [Input('refresh-button', 'n_clicks'),
     Input('interval-component', 'n_intervals')]
)
def update_charts(n_clicks, n_intervals):
    df = load_data()
    
    # Ensure data types are correct
    df['stars'] = df['stars'].fillna(0).astype(int)
    df['star_change'] = df['star_change'].fillna(0).astype(int)
    df['contributor_count'] = df['contributor_count'].fillna(0).astype(int)
    
    # Calculate summary statistics
    total_repos = len(df)
    total_stars = df['star_change'].sum()
    avg_contributors = df['contributor_count'].mean()
    unique_languages = df['language'].nunique()
    
    summary_stats = []
    for title, value, icon in [
        ('Total Repositories', f'{total_repos:,}', '📚'),
        ('Total Stars Gained', f'{total_stars:,}', '⭐'),
        ('Avg Contributors', f'{avg_contributors:.1f}', '👥'),
        ('Unique Languages', str(unique_languages), '💻')
    ]:
        summary_stats.append(html.Div([
            html.Div(icon, style={
                'fontSize': '2rem',
                'marginBottom': '10px'
            }),
            html.H4(title, style={
                'color': '#24292e',
                'fontSize': '1.1rem',
                'marginBottom': '8px'
            }),
            html.P(value, style={
                'fontSize': '1.8rem',
                'fontWeight': '600',
                'color': '#2ea44f',
                'margin': '0'
            })
        ], style={
            'textAlign': 'center',
            'padding': '25px',
            'backgroundColor': '#ffffff',
            'borderRadius': '12px',
            'boxShadow': '0 4px 12px rgba(0,0,0,0.05)',
            'border': '1px solid #e1e4e8',
            'transition': 'transform 0.2s ease, box-shadow 0.2s ease',
            'hover': {
                'transform': 'translateY(-5px)',
                'boxShadow': '0 8px 16px rgba(0,0,0,0.1)'
            }
        }))
    
    last_update = f'Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
    
    return [
        create_language_trend_chart(df),
        create_star_changes_chart(df),
        create_stars_contributors_chart(df),
        last_update,
        summary_stats
    ]

def main():
    app.run_server(debug=True)

if __name__ == '__main__':
    main()