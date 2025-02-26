# scripts/scraper.py
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os

from db_utils import init_db, append_data_to_db

def scrape_github_trending(url="https://github.com/trending"):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        print("[DEBUG] Successfully fetched trending page")
    except requests.RequestException as e:
        print(f"[ERROR] Failed to fetch trending page: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    repo_list = soup.find_all("article", class_="Box-row")
    print(f"[DEBUG] Found {len(repo_list)} repositories")

    data = []
    for repo in repo_list:
        full_name_tag = repo.find("h2", class_="h3")
        full_name = (
            full_name_tag.get_text(strip=True)
            .replace("\n", "")
            .replace(" ", "")
        )
        print(f"\n[DEBUG] Processing repository: {full_name}")

        desc_tag = repo.find("p", class_="col-9")
        description = desc_tag.get_text(strip=True) if desc_tag else ""
        lang_tag = repo.find("span", itemprop="programmingLanguage")
        language = lang_tag.get_text(strip=True) if lang_tag else ""

        star_tag = repo.find("a", href=lambda href: href and href.endswith("/stargazers"))
        raw_stars = star_tag.get_text(strip=True) if star_tag else "0"
        stars = convert_star_str_to_int(raw_stars)

        star_change_tag = repo.find("span", class_="d-inline-block float-sm-right")
        raw_star_change = star_change_tag.get_text(strip=True) if star_change_tag else "0"
        star_change = convert_star_str_to_int(raw_star_change.split()[0]) if raw_star_change != "0" else 0

        # Get topics with more specific selectors and debug info
        topics = []
        # Try finding topics in the main repository description area
        topics_container = repo.find('div', {'class': ['f6', 'color-fg-muted', 'mt-2']})
        if topics_container:
            print("[DEBUG] Found topics container")
            # Print the HTML content of the topics container for debugging
            print(f"[DEBUG] Topics container HTML: {topics_container}")
            
            # Try multiple selectors for topic tags
            topic_tags = topics_container.select('a[data-ga-click*="topic_tag"]')
            if not topic_tags:
                topic_tags = topics_container.find_all('a', class_='topic-tag')
            if not topic_tags:
                topic_tags = topics_container.select('a[href*="/topics/"]')
                
            if topic_tags:
                topics = [tag.get_text(strip=True) for tag in topic_tags if tag.get_text(strip=True)]
                print(f"[DEBUG] Found topics: {topics}")

        # If no topics found, try alternative selectors
        if not topics:
            print("[DEBUG] Trying alternative topic selectors")
            # Try finding topics in any location
            all_topic_tags = repo.select('a[data-ga-click*="topic_tag"], a.topic-tag, a[href*="/topics/"]')
            if all_topic_tags:
                topics = [tag.get_text(strip=True) for tag in all_topic_tags if tag.get_text(strip=True)]
                print(f"[DEBUG] Found topics with alternative selector: {topics}")

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
                        print(f"[WARNING] Invalid contributor count for {full_name}")
        except requests.RequestException as e:
            print(f"[WARNING] Failed to fetch contributors for {full_name}: {e}")

        link = "https://github.com/" + full_name
        data.append({
            'full_name': full_name,
            'description': description,
            'language': language,
            'stars': stars,
            'star_change': star_change,
            'topics': ','.join(topics),
            'contributor_count': contributor_count,
            'link': link
        })

    print(f"\n[DEBUG] Total repositories processed: {len(data)}")
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
