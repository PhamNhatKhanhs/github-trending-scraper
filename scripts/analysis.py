# scripts/analysis.py
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from db_utils import get_data_from_db

def analyze_by_date():
    # Get data from database
    df = get_data_from_db()
    if df.empty:
        print("No data found in the database. Please run the scraper first.")
        return
    # Convert scrape_date to datetime
    df["scrape_date"] = pd.to_datetime(df["scrape_date"])
    
    # 1. Language Distribution Analysis
    plt.figure(figsize=(12, 6))
    lang_counts = df['language'].value_counts().head(15)
    if not lang_counts.empty:
        sns.barplot(x=lang_counts.values, y=lang_counts.index)
        plt.title('Most Used Programming Languages')
        plt.xlabel('Number of Repositories')
        plt.tight_layout()
        plt.savefig('data/language_distribution.png')
    plt.close()
    # 2. Star Changes Analysis
    plt.figure(figsize=(12, 6))
    df_sorted = df.sort_values('star_change', ascending=False).head(15)
    sns.barplot(x='star_change', y='full_name', data=df_sorted)
    plt.title('Repositories with Most Star Changes')
    plt.xlabel('Star Change')
    plt.tight_layout()
    plt.savefig('data/star_changes.png')
    plt.close()
    # 3. Contributor Analysis
    plt.figure(figsize=(12, 6))
    df_sorted = df.sort_values('contributor_count', ascending=False).head(15)
    sns.barplot(x='contributor_count', y='full_name', data=df_sorted)
    plt.title('Repositories with Most Contributors')
    plt.xlabel('Number of Contributors')
    plt.tight_layout()
    plt.savefig('data/contributor_analysis.png')
    plt.close()
    # Generate summary report
    with open('data/analysis_report.md', 'w', encoding='utf-8') as f:
        f.write('# GitHub Trending Analysis Report\n\n')
        f.write(f'Report generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n\n')
        
        f.write('## Key Findings\n\n')
        if not lang_counts.empty:
            f.write(f'1. Most Popular Language: {lang_counts.index[0]} with {lang_counts.values[0]} repositories\n')
        
        top_star_change = df_sorted.iloc[0]
        f.write(f'2. Repository with Most Star Changes: {top_star_change["full_name"]} with {top_star_change["star_change"]} stars\n')
        
        top_contributors = df.nlargest(1, 'contributor_count').iloc[0]
        f.write(f'3. Repository with Most Contributors: {top_contributors["full_name"]} with {top_contributors["contributor_count"]} contributors\n')
def main():
    print("=== Starting GitHub Trending Analysis ===")
    analyze_by_date()
    print("=== Analysis Complete ===")
    print("Check the 'data' directory for visualization results and the analysis report.")

if __name__ == "__main__":
    main()
