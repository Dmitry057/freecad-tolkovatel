import time
import requests
from bs4 import BeautifulSoup
import urllib.parse
import json

BASE_URL = "https://forum.freecad.org"   # Main domain
SUBFORUM_URL = "https://forum.freecad.org/viewforum.php?f=3"  # Example subforum URL

# Set user-agent to identify your script politely
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) MyScraper/1.0"
}

def get_soup(url):
    """Return BeautifulSoup object for the given URL."""
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")

def parse_subforum_page(subforum_url):
    """
    Parse a single 'subforum page' and return:
    - A list of (topic_title, topic_url)
    - The next page URL (or None if no more pages)
    """
    soup = get_soup(subforum_url)

    # Example selector for topics in phpBB
    topic_rows = soup.select("ul.topiclist.topics li dl dt a.topictitle")
    
    topics = []
    for link in topic_rows:
        topic_title = link.text.strip()
        topic_href = link.get("href")
        topic_url = urllib.parse.urljoin(BASE_URL, topic_href)
        topics.append((topic_title, topic_url))

    # Attempt to find the link to the "next page"
    next_page_link = soup.select_one("a[rel='next']")
    if next_page_link:
        next_page_url = urllib.parse.urljoin(BASE_URL, next_page_link.get("href"))
    else:
        next_page_url = None

    return topics, next_page_url

def parse_topic(topic_url):
    """
    Parse a topic page (a thread) to extract all posts on that page:
    Return:
    - A list of dicts: { 'author': ..., 'content': ..., 'date': ... }
    - Next page URL if more pages in the topic, else None
    """
    soup = get_soup(topic_url)

    # Each post is typically inside something like <div class="post"> or <div id="pXXXX">
    post_divs = soup.select("div.post")
    
    posts = []
    for post_div in post_divs:

        # Author
        author_element = post_div.select_one(".username")
        author = author_element.get_text(strip=True) if author_element else "Unknown"

        # Date/time
        date_element = post_div.select_one(".author")
        # Usually something like "Posted: Fri Sep 30, 2022 5:00 pm"
        date_text = date_element.get_text(strip=True) if date_element else "Unknown"

        # Post content
        content_div = post_div.select_one(".content")
        if content_div:
            # remove any quoted text or just keep the raw HTML
            content_text = content_div.get_text(strip=True)
        else:
            content_text = "No content"

        posts.append(
            {
             "author": author,
             "date": date_text,
             "content": content_text
            }
        )

    # Check if there's a "next page" of the same thread
    next_topic_page_link = soup.select_one("a[rel='next']")
    if next_topic_page_link:
        next_topic_page_url = urllib.parse.urljoin(BASE_URL, next_topic_page_link.get("href"))
    else:
        next_topic_page_url = None

    return posts, next_topic_page_url

def scrape_subforum(subforum_url, max_pages=5, delay=0.1):
    """
    Scrape the given subforum, iterating through multiple pages.
    max_pages: how many pages to scrape (to avoid infinite loops)
    delay: seconds to wait between requests (be polite)
    """
    all_topics = []
    page_url = subforum_url
    pages_scraped = 0

    while page_url and pages_scraped < max_pages:
        print(f"Scraping subforum page: {page_url}")
        topics, next_page = parse_subforum_page(page_url)
        all_topics.extend(topics)

        page_url = next_page
        pages_scraped += 1
        time.sleep(delay)

    return all_topics

def scrape_topic(topic_url, max_pages=5, delay=0.1):
    """
    Scrape an individual topic across multiple pages.
    max_pages: avoid infinite loops
    delay: polite sleeping
    """
    all_posts = []
    current_page_url = topic_url
    pages_scraped = 0

    while current_page_url and pages_scraped < max_pages:
        print(f"Scraping topic page: {current_page_url}")
        posts, next_page = parse_topic(current_page_url)
        all_posts.extend(posts)

        current_page_url = next_page
        pages_scraped += 1
        time.sleep(delay)

    return all_posts

def main():
    # 1. Scrape subforum pages to get topics
    topics_data = scrape_subforum(SUBFORUM_URL, max_pages=1000)
    print(f"Found {len(topics_data)} topics (limited by max_pages=3).")

    # 2. For each topic, scrape the posts
    #    (Be cautious if you have thousands of topics!)

    all_posts = []
    for topic_title, topic_url in topics_data:  # limit to first 5 topics for demo
        print(f"\nScraping topic: {topic_title}\nURL: {topic_url}")
        posts = scrape_topic(topic_url, max_pages=1000)
        print(f"  --> Collected {len(posts)} posts from '{topic_title}'.")
        # Append results to a JSON file
        with open("collected_forum_data/all_posts.json", "a") as file:
            json.dump({
            "title": topic_title,
            "chat": posts
            }, file, indent=4)
            file.write(",\n")

    with open("collected_forum_data/all_posts.json", "a") as file:
            file.write("]")
if __name__ == "__main__":
    main()

'''
forum_data = 
[
    {
        'title',
        content[]
    }
]
'''