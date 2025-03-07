# scripts/notifier.py
# Mô-đun gửi thông báo về những thay đổi đáng chú ý trên GitHub Trending
# Phân tích và gửi email thông báo về các ngôn ngữ mới, sự thay đổi số sao và chủ đề mới

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import pandas as pd
import sqlite3
from dotenv import load_dotenv
from db_utils import DB_PATH

load_dotenv()

def get_trend_changes():
    # Hàm phân tích và lấy các thay đổi đáng chú ý từ dữ liệu GitHub Trending
    # Trả về:
    #   Danh sách các thay đổi quan trọng (ngôn ngữ mới, tăng số sao, chủ đề mới)
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql("""
            SELECT * FROM github_trending 
            WHERE scrape_date >= date('now', '-1 day')
            ORDER BY scrape_date DESC
        """, conn)
        conn.close()
    except Exception as e:
        print(f"[ERROR] Failed to fetch trend changes: {e}")
        return None
    
    if df.empty:
        return None
        
    # Analyze significant changes
    significant_changes = []
    
    # 1. New languages in trending
    if not df.empty and len(df) > 1:
        latest_languages = set(df.iloc[0]['language'].split(',') if df.iloc[0]['language'] else [])
        previous_languages = set(df.iloc[-1]['language'].split(',') if df.iloc[-1]['language'] else [])
        new_languages = latest_languages - previous_languages
        if new_languages:
            significant_changes.append(f"New trending languages: {', '.join(new_languages)}")
    
    # 2. Repositories with dramatic star increases
    high_star_changes = df[df['star_change'] > 1000][['full_name', 'star_change']]
    if not high_star_changes.empty:
        for _, repo in high_star_changes.iterrows():
            significant_changes.append(
                f"Repository {repo['full_name']} gained {repo['star_change']} stars"
            )
    
    # 3. New trending topics
    if not df.empty and len(df) > 1:
        latest_topics = set()
        previous_topics = set()
        if not pd.isna(df.iloc[0]['topics']):
            latest_topics.update(t.strip() for t in df.iloc[0]['topics'].split(',') if t.strip())
        if not pd.isna(df.iloc[-1]['topics']):
            previous_topics.update(t.strip() for t in df.iloc[-1]['topics'].split(',') if t.strip())
        new_topics = latest_topics - previous_topics
        if new_topics:
            significant_changes.append(f"New trending topics: {', '.join(new_topics)}")
    
    return significant_changes

def send_notification(changes):
    # Hàm gửi email thông báo về các thay đổi đáng chú ý
    # Tham số:
    #   changes: Danh sách các thay đổi cần thông báo
    if not changes:
        return
        
    sender_email = os.getenv('SENDER_EMAIL')
    sender_password = os.getenv('SENDER_PASSWORD')
    recipient_email = os.getenv('RECIPIENT_EMAIL')
    
    if not all([sender_email, sender_password, recipient_email]):
        print("[ERROR] Email configuration missing. Please check .env file.")
        return
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = f'GitHub Trending Alert - {datetime.now().strftime("%Y-%m-%d")}'
    
    body = "\n\n".join(["GitHub Trending Significant Changes:", *changes])
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        print("[INFO] Notification email sent successfully")
    except Exception as e:
        print(f"[ERROR] Failed to send notification: {str(e)}")

def main():
    # Hàm chính để kiểm tra và gửi thông báo về các thay đổi
    print("=== Checking for Significant Changes ===")
    changes = get_trend_changes()
    if changes:
        send_notification(changes)
        print(f"Found {len(changes)} significant changes")
    else:
        print("No significant changes detected")

if __name__ == '__main__':
    main()