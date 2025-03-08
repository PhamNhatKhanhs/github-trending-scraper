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
    # Phần header với nền gradient
    html.Div([
        html.H1('Phân Tích GitHub Trending', 
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
    
    # Bảng thống kê tổng quan với layout grid cải tiến
    html.Div([
        html.Div([
            html.H3('Thống Kê Tổng Quan', 
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
    
    # Nút làm mới và thời gian cập nhật cuối với style cải tiến
    html.Div([
        html.Button(
            'Làm Mới Dữ Liệu',
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
    
    # Các tab với style cải tiến
    dcc.Tabs([
        dcc.Tab(
            label='Xu Hướng Ngôn Ngữ',
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
            label='Thay Đổi Star',
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
            label='Star và Người Đóng Góp',
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
    
    # Cập nhật tự động mỗi 5 phút
    dcc.Interval(
        id='interval-component',
        interval=300000,  # cập nhật mỗi 5 phút
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
    """
    Tải dữ liệu từ cơ sở dữ liệu và xử lý
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql("SELECT * FROM repositories", conn)
        conn.close()
        
        if df.empty:
            print("Cảnh báo: Không tìm thấy dữ liệu trong cơ sở dữ liệu")
            return pd.DataFrame()
            
        # Xử lý dữ liệu ngày tháng
        df['scrape_date'] = pd.to_datetime(df['scrape_date'], errors='coerce')
        df = df.dropna(subset=['scrape_date'])
        
        # Xử lý dữ liệu số
        df['language'] = df['language'].fillna('Không xác định')
        df['star_change'] = pd.to_numeric(df['star_change'], errors='coerce').fillna(0)
        df['contributor_count'] = pd.to_numeric(df['contributor_count'], errors='coerce').fillna(0)
        df['stars'] = pd.to_numeric(df['stars'], errors='coerce').fillna(0)
        
        # Chuyển đổi kiểu dữ liệu
        df['star_change'] = df['star_change'].astype(int)
        df['contributor_count'] = df['contributor_count'].astype(int)
        df['stars'] = df['stars'].astype(int)
        
        return df
    except sqlite3.Error as e:
        print(f"Lỗi cơ sở dữ liệu: {e}")
        return pd.DataFrame()
    except Exception as e:
        print(f"Lỗi khi tải dữ liệu: {e}")
        return pd.DataFrame()

def create_language_trend_chart(df):
    """
    Tạo biểu đồ xu hướng ngôn ngữ lập trình
    """
    # Lấy 10 ngôn ngữ phổ biến nhất
    top_languages = df.groupby('language').size().nlargest(10).index
    df_filtered = df[df['language'].isin(top_languages)]
    lang_trend = df_filtered.groupby(['scrape_date', 'language']).size().reset_index(name='count')
    
    # Tạo biểu đồ
    fig = px.area(lang_trend, x='scrape_date', y='count', color='language',
                  title='Xu Hướng Ngôn Ngữ Lập Trình',
                  groupnorm='percent')
    
    # Cập nhật layout
    fig.update_layout(
        template='plotly_white',
        title_x=0.5,
        title_font_size=24,
        title_font_family='Segoe UI',
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis_title='Ngày',
        yaxis_title='Phần Trăm',
        legend_title='Ngôn Ngữ',
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
    """
    Tạo biểu đồ thay đổi star theo ngôn ngữ
    """
    # Tính trung bình thay đổi star cho mỗi ngôn ngữ
    star_changes = df.groupby('language')['star_change'].mean().sort_values(ascending=False).head(10)
    star_df = pd.DataFrame({'language': star_changes.index, 'avg_stars': star_changes.values})
    
    # Tạo biểu đồ
    fig = px.bar(star_df, x='language', y='avg_stars',
                 title='Trung Bình Thay Đổi Star Theo Ngôn Ngữ')
    
    # Cập nhật layout
    fig.update_layout(
        template='plotly_white',
        title_x=0.5,
        title_font_size=24,
        title_font_family='Segoe UI',
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis_title='Ngôn Ngữ Lập Trình',
        yaxis_title='Trung Bình Thay Đổi Star',
        showlegend=False,
        bargap=0.2,
        font_family='Segoe UI'
    )
    return fig

def create_stars_contributors_chart(df):
    """
    Tạo biểu đồ phân tán giữa số star và số người đóng góp
    """
    # Tạo biểu đồ phân tán
    fig = px.scatter(
        df,
        x='stars',
        y='contributor_count',
        color='language',
        title='Star và Người Đóng Góp Theo Ngôn Ngữ',
        hover_data=['full_name', 'star_change'],
        labels={
            'stars': 'Tổng Số Star',
            'contributor_count': 'Số Người Đóng Góp',
            'language': 'Ngôn Ngữ Lập Trình',
            'full_name': 'Repository',
            'star_change': 'Thay Đổi Star'
        },
        color_discrete_sequence=px.colors.qualitative.Set3
    )

    # Cập nhật layout
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

    # Cập nhật hiển thị tooltip
    fig.update_traces(
        marker=dict(size=10, opacity=0.7),
        hovertemplate='<b>%{customdata[0]}</b><br>'
                      'Star: %{x:,}<br>'
                      'Người đóng góp: %{y:,}<br>'
                      'Thay đổi star: %{customdata[1]:+,}<br>'
                      'Ngôn ngữ: %{marker.color}<extra></extra>'
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
    """
    Cập nhật tất cả các biểu đồ và thống kê
    """
    df = load_data()
    
    # Tính toán thống kê tổng quan
    total_repos = len(df)
    total_stars = df['star_change'].sum()
    avg_contributors = df['contributor_count'].mean()
    unique_languages = df['language'].nunique()
    
    # Tạo các thẻ thống kê
    summary_stats = []
    for title, value, icon in [
        ('Tổng Số Repository', f'{total_repos:,}', '📚'),
        ('Tổng Star Mới', f'{total_stars:,}', '⭐'),
        ('Trung Bình Người Đóng Góp', f'{avg_contributors:.1f}', '👥'),
        ('Số Ngôn Ngữ', str(unique_languages), '💻')
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
    
    last_update = f'Cập nhật lần cuối: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
    
    return [
        create_language_trend_chart(df),
        create_star_changes_chart(df),
        create_stars_contributors_chart(df),
        last_update,
        summary_stats
    ]

def main():
    """
    Hàm chính để chạy ứng dụng
    """
    app.run_server(debug=True)

if __name__ == '__main__':
    main()