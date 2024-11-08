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

# 8ビット風のカラーパレット（例）
colors = [
    "#FFB6C1", "#FF69B4", "#DB7093", "#C71585", "#FF6347",
    "#FFA500", "#FFD700", "#FFFF00", "#ADFF2F", "#7FFF00",
    "#32CD32", "#00FF7F", "#3CB371", "#20B2AA", "#00CED1",
]

def save_language_pie_chart(language_usage):
    labels = []
    sizes = []
    filtered_labels = []
    filtered_sizes = []
    threshold = 5  # %が5%以下のラベルを非表示にする

    # 言語データのフィルタリングとラベル設定
    for language, size in language_usage.items():
        labels.append(language)
        sizes.append(size)
        if size >= threshold:
            filtered_labels.append(f"{language} ({size}%)")
            filtered_sizes.append(size)
        else:
            # 表示されない小さな項目は「その他」にまとめるオプションもあります
            filtered_labels.append("")
            filtered_sizes.append(size)

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(aspect="equal"))

    wedges, texts = ax.pie(
        filtered_sizes,
        startangle=140,
        colors=colors[:len(filtered_labels)],  # 8ビット風カラーパレットを適用
        wedgeprops=dict(width=0.3, edgecolor='w'),  # 3D風の立体感
    )

    # レジェンドの設定
    ax.legend(wedges, labels, title="Languages", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))

    # タイトルと見た目の調整
    ax.set_title("3D-Style Language Usage Chart", pad=20, fontsize=14, fontweight="bold", color="#4B0082")
    fig.patch.set_facecolor("#333333")  # 背景色をダークにして8ビット風に
    plt.gcf().canvas.draw()  # キャンバスを更新

    # 画像の保存
    plt.savefig("language_usage.png", format="png", bbox_inches="tight", transparent=True)
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
