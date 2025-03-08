# scripts/scraper.py
# Mô-đun thu thập dữ liệu từ trang GitHub Trending
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os

from db_utils import init_db, append_data_to_db

def scrape_github_trending(url="https://github.com/trending"):
    """
    Thu thập thông tin các repository đang thịnh hành trên GitHub
    
    Tham số:
        url: Đường dẫn đến trang GitHub Trending (mặc định: https://github.com/trending)
    
    Trả về:
        Danh sách các repository với thông tin chi tiết
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        print("[INFO] Đã tải thành công trang trending")
    except requests.RequestException as e:
        print(f"[LỖI] Không thể tải trang trending: {e}")
        return []

    # Phân tích cú pháp HTML và tìm tất cả các repository
    soup = BeautifulSoup(response.text, "html.parser")
    repo_list = soup.find_all("article", class_="Box-row")
    print(f"[INFO] Tìm thấy {len(repo_list)} repository")

    data = []
    for repo in repo_list:
        # Lấy tên đầy đủ của repository
        full_name_tag = repo.find("h2", class_="h3")
        full_name = (
            full_name_tag.get_text(strip=True)
            .replace("\n", "")
            .replace(" ", "")
        )

        # Lấy mô tả và ngôn ngữ lập trình của repository
        desc_tag = repo.find("p", class_="col-9")
        description = desc_tag.get_text(strip=True) if desc_tag else ""
        lang_tag = repo.find("span", itemprop="programmingLanguage")
        language = lang_tag.get_text(strip=True) if lang_tag else ""

        # Lấy số lượng sao và sự thay đổi số sao
        star_tag = repo.find("a", href=lambda href: href and href.endswith("/stargazers"))
        raw_stars = star_tag.get_text(strip=True) if star_tag else "0"
        stars = convert_star_str_to_int(raw_stars)

        star_change_tag = repo.find("span", class_="d-inline-block float-sm-right")
        raw_star_change = star_change_tag.get_text(strip=True) if star_change_tag else "0"
        star_change = convert_star_str_to_int(raw_star_change.split()[0]) if raw_star_change != "0" else 0

        # Lấy số lượng người đóng góp
        contributors_url = f"https://github.com/{full_name}/contributors"
        contributor_count = 0
        try:
            contributors_response = requests.get(contributors_url, timeout=5)
            if contributors_response.status_code == 200:
                contributors_soup = BeautifulSoup(contributors_response.text, "html.parser")
                contributor_count_tag = contributors_soup.find("span", class_="Counter")
                if contributor_count_tag:
                    try:
                        contributor_count = int(contributor_count_tag.get_text(strip=True))
                    except ValueError:
                        print(f"[CẢNH BÁO] Số lượng người đóng góp không hợp lệ cho {full_name}")
        except requests.RequestException as e:
            print(f"[CẢNH BÁO] Không thể lấy thông tin người đóng góp cho {full_name}: {e}")

        # Tạo đường dẫn đến repository và thêm vào danh sách kết quả
        link = "https://github.com/" + full_name
        data.append({
            'full_name': full_name,
            'description': description,
            'language': language,
            'stars': stars,
            'star_change': star_change,
            'contributor_count': contributor_count,
            'link': link
        })

    print(f"[INFO] Tổng số repository đã xử lý: {len(data)}")
    return data

def convert_star_str_to_int(star_str):
    """
    Chuyển đổi chuỗi số sao thành số nguyên
    
    Ví dụ: 
        "1.2k" -> 1200
        "500" -> 500
    """
    star_str = star_str.lower().replace(",", "")
    if "k" in star_str:
        num = float(star_str.replace("k", "")) * 1000
    else:
        num = float(star_str)
    return int(num)

def main():
    """
    Hàm chính để thực thi quá trình thu thập dữ liệu
    """
    print("=== Bắt đầu thu thập dữ liệu từ GitHub Trending ===")
    init_db()

    # Thu thập dữ liệu và lưu vào cơ sở dữ liệu
    data = scrape_github_trending("https://github.com/trending")
    print(f"[INFO] Đã lấy được {len(data)} repository")

    df = pd.DataFrame(data)
    df["scrape_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    append_data_to_db(df)
    print("=== Hoàn thành ===")

if __name__ == "__main__":
    main()
