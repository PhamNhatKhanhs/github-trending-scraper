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
    """
    Phân tích và lấy các thay đổi đáng chú ý từ dữ liệu GitHub Trending
    
    Trả về:
        Danh sách các thay đổi quan trọng (ngôn ngữ mới, tăng số sao, chủ đề mới)
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql("""
            SELECT * FROM repositories 
            WHERE scrape_date >= date('now', '-1 day')
            ORDER BY scrape_date DESC
        """, conn)
        conn.close()
    except Exception as e:
        print(f"[LỖI] Không thể lấy dữ liệu thay đổi: {e}")
        return None
    
    if df.empty:
        return None
        
    # Phân tích các thay đổi quan trọng
    significant_changes = []
    
    # 1. Các ngôn ngữ mới trong trending
    if not df.empty and len(df) > 1:
        latest_languages = set(df.iloc[0]['language'].split(',') if df.iloc[0]['language'] else [])
        previous_languages = set(df.iloc[-1]['language'].split(',') if df.iloc[-1]['language'] else [])
        new_languages = latest_languages - previous_languages
        if new_languages:
            significant_changes.append(f"Ngôn ngữ mới trong trending: {', '.join(new_languages)}")
    
    # 2. Repository có số star tăng đột biến
    high_star_changes = df[df['star_change'] > 1000][['full_name', 'star_change']]
    if not high_star_changes.empty:
        for _, repo in high_star_changes.iterrows():
            significant_changes.append(
                f"Repository {repo['full_name']} tăng {repo['star_change']} star"
            )
    
    # 3. Chủ đề mới trong trending
    if not df.empty and len(df) > 1:
        latest_topics = set()
        previous_topics = set()
        if not pd.isna(df.iloc[0]['topics']):
            latest_topics.update(t.strip() for t in df.iloc[0]['topics'].split(',') if t.strip())
        if not pd.isna(df.iloc[-1]['topics']):
            previous_topics.update(t.strip() for t in df.iloc[-1]['topics'].split(',') if t.strip())
        new_topics = latest_topics - previous_topics
        if new_topics:
            significant_changes.append(f"Chủ đề mới trong trending: {', '.join(new_topics)}")
    
    return significant_changes

def send_notification(changes):
    """
    Gửi email thông báo về các thay đổi đáng chú ý
    
    Tham số:
        changes: Danh sách các thay đổi cần thông báo
    """
    if not changes:
        return
        
    sender_email = os.getenv('SENDER_EMAIL')
    sender_password = os.getenv('SENDER_PASSWORD')
    recipient_email = os.getenv('RECIPIENT_EMAIL')
    
    if not all([sender_email, sender_password, recipient_email]):
        print("[LỖI] Thiếu cấu hình email. Vui lòng kiểm tra file .env")
        return
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = f'Thông Báo GitHub Trending - {datetime.now().strftime("%Y-%m-%d")}'
    
    body = "\n\n".join(["Những Thay Đổi Quan Trọng Trên GitHub Trending:", *changes])
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        print("[INFO] Đã gửi email thông báo thành công")
    except Exception as e:
        print(f"[LỖI] Không thể gửi thông báo: {str(e)}")

def main():
    """
    Hàm chính để kiểm tra và gửi thông báo về các thay đổi
    """
    print("=== Kiểm Tra Các Thay Đổi Quan Trọng ===")
    changes = get_trend_changes()
    if changes:
        send_notification(changes)
        print(f"Tìm thấy {len(changes)} thay đổi quan trọng")
    else:
        print("Không phát hiện thay đổi quan trọng nào")

if __name__ == '__main__':
    main()