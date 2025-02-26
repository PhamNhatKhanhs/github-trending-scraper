# scripts/scraper.py
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os

from db_utils import init_db, append_data_to_db

def scrape_github_trending(url="https://github.com/trending"):
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    repo_list = soup.find_all("article", class_="Box-row")

    data = []
    for repo in repo_list:
        full_name_tag = repo.find("h2", class_="h3")
        # "username/reponame" (cắt khoảng trắng)
        full_name = (
            full_name_tag.get_text(strip=True)
            .replace("\n", "")
            .replace(" ", "")
        )
        desc_tag = repo.find("p", class_="col-9")
        description = desc_tag.get_text(strip=True) if desc_tag else ""
        lang_tag = repo.find("span", itemprop="programmingLanguage")
        language = lang_tag.get_text(strip=True) if lang_tag else ""

        star_tag = repo.find("a", href=lambda href: href and href.endswith("/stargazers"))
        raw_stars = star_tag.get_text(strip=True) if star_tag else "0"
        stars = convert_star_str_to_int(raw_stars)

        link = "https://github.com/" + full_name

        data.append({
            "full_name": full_name,
            "description": description,
            "language": language,
            "stars": stars,
            "link": link,
        })

    return data

def convert_star_str_to_int(star_str):
    star_str = star_str.lower().replace(",", "")
    if "k" in star_str:
        num = float(star_str.replace("k", "")) * 1000
    else:
        num = float(star_str)
    return int(num)

def main():
    print("=== Start Scraping GitHub Trending ===")
    # Khởi tạo DB + bảng (nếu chưa có)
    init_db()

    data = scrape_github_trending("https://github.com/trending")
    print(f"[INFO] Lấy được {len(data)} repositories")

    # Tạo DataFrame và thêm cột scrape_date
    df = pd.DataFrame(data)
    df["scrape_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Append vào bảng
    append_data_to_db(df)

    print("=== Done ===")

if __name__ == "__main__":
    main()
