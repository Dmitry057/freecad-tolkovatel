import json

def remove_repetitions(file_path):
    with open(file_path, 'r') as file:
        posts = json.load(file)
    
    seen_titles = set()
    unique_posts = []

    for post in posts:
        title = post['title']
        if title not in seen_titles:
            seen_titles.add(title)
            unique_posts.append(post)
    
    with open(file_path, 'w') as file:
        json.dump(unique_posts, file, indent=4)

if __name__ == "__main__":
    remove_repetitions('/Users/dmitry057/Projects/DeepL/easy-local-rag/collected_forum_data/all_posts.json')