import requests
from collections import defaultdict
import json
import os
import matplotlib.pyplot as plt
from datetime import datetime

def fetch_repositories():
    url = 'https://api.github.com/user/repos'
    headers = {
        'Authorization': f'token {os.getenv("GITHUB_TOKEN")}'
    }
    params = {
        'per_page': 100,
        'type': 'all'
    }
    repos = []
    while url:
        response = requests.get(url, headers=headers, params=params)
        response_data = response.json()
        repos.extend(response_data)
        url = response.links.get('next', {}).get('url')
    return repos

def fetch_languages(repo):
    url = repo['languages_url']
    headers = {
        'Authorization': f'token {os.getenv("GITHUB_TOKEN")}'
    }
    response = requests.get(url, headers=headers)
    return response.json()

def calculate_language_usage(repositories):
    language_count = defaultdict(int)
    total_bytes = 0
    for repo in repositories:
        languages = fetch_languages(repo)
        for language, bytes_count in languages.items():
            language_count[language] += bytes_count
            total_bytes += bytes_count
    return {language: round((bytes_count / total_bytes) * 100, 2) for language, bytes_count in language_count.items()}

def save_language_pie_chart(language_usage):
    labels = list(language_usage.keys())
    sizes = list(language_usage.values())

    plt.figure(figsize=(6, 6))  # グラフ画像を小さめに設定
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, 
            textprops={'fontsize': 10})  # フォントサイズを小さく調整
    plt.axis('equal')  # 円形に調整
    plt.title("Language Usage", fontsize=14)
    
    # レジェンドを追加してラベルが重ならないようにする
    plt.legend(labels, loc="best", fontsize=10, bbox_to_anchor=(1, 0.5))
    plt.tight_layout()  # レイアウトを自動調整

    plt.savefig("language_usage.png", bbox_inches='tight')  # 画像を保存
    plt.close()

def save_readme(language_usage):
    # 現在の日時を取得
    update_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')

    with open("README.md", "w") as f:
        f.write("# Language Usage\n\n")
        f.write(f"Last updated: {update_time}\n\n")
        
        # 言語とその割合を記載
        for language, percentage in language_usage.items():
            f.write(f"- {language}: {percentage}%\n")
        
        f.write("\n![Language Usage Chart](language_usage.png)\n")

def main():
    repositories = fetch_repositories()
    language_usage = calculate_language_usage(repositories)
    
    with open("language_usage.json", "w") as f:
        json.dump(language_usage, f)
    
    # 言語使用率の円グラフとREADMEの保存
    save_language_pie_chart(language_usage)
    save_readme(language_usage)

if __name__ == "__main__":
    main()
