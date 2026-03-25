import os
import requests
from datetime import datetime, timedelta


NEWSAPI_ENDPOINT = "https://newsapi.org/v2/everything"

# (query, source_region)
QUERIES = [
    # India-perspective
    ("India Germany trade import export", "India"),
    ("India EU import Germany", "India"),
    ("India European Union export Germany", "India"),
    ("India EU FTA free trade agreement", "India"),
    ("India Germany business opportunity", "India"),
    ("India EU tariff customs duty", "India"),
    ("Germany import India products", "India"),
    ("India export Europe opportunity", "India"),
    # EU-perspective
    ("Germany India trade 2025", "EU"),
    ("EU India trade agreement news", "EU"),
    ("European Union Asia trade policy", "EU"),
    ("Germany export Asia opportunity", "EU"),
    ("EU India investment news", "EU"),
]


def fetch_articles() -> list[dict]:
    api_key = os.environ.get("NEWSAPI_KEY", "")
    if not api_key:
        print("[NewsAPI] NEWSAPI_KEY not set — skipping.")
        return []

    from_date = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")
    seen_urls = set()
    articles = []

    for query, source_region in QUERIES:
        params = {
            "q": query,
            "from": from_date,
            "sortBy": "relevancy",
            "language": "en",
            "pageSize": 10,
            "apiKey": api_key,
        }
        try:
            resp = requests.get(NEWSAPI_ENDPOINT, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            for item in data.get("articles", []):
                url = item.get("url", "")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    articles.append({
                        "title": item.get("title", ""),
                        "url": url,
                        "source": item.get("source", {}).get("name", "NewsAPI"),
                        "source_region": source_region,
                        "published_at": item.get("publishedAt", ""),
                        "description": item.get("description", "") or "",
                    })
        except Exception as exc:
            print(f"[NewsAPI] Error fetching '{query}': {exc}")

    print(f"[NewsAPI] Fetched {len(articles)} articles.")
    return articles
