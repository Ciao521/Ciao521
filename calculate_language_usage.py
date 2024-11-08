import requests
from collections import defaultdict
import json
import os

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
        # デバッグ用: レスポンス内容を出力
        print(response_data)  # この行を追加
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

def main():
    repositories = fetch_repositories()
    language_usage = calculate_language_usage(repositories)
    with open("language_usage.json", "w") as f:
        json.dump(language_usage, f)

if __name__ == "__main__":
    main()
