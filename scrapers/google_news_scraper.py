import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus


SEARCH_QUERIES = [
    "India Germany trade news today",
    "India EU import export opportunity 2025",
    "India Germany business deal latest",
    "Germany import India products 2025",
    "India European Union FTA trade update",
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}


def fetch_articles() -> list[dict]:
    seen_urls = set()
    articles = []

    for query in SEARCH_QUERIES:
        url = f"https://news.google.com/search?q={quote_plus(query)}&hl=en-IN&gl=IN&ceid=IN:en"
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            for article_tag in soup.select("article")[:8]:
                title_tag = article_tag.find("a", class_=lambda c: c and "title" in c.lower()) \
                            or article_tag.find("h3") \
                            or article_tag.find("h4")
                link_tag = article_tag.find("a", href=True)
                time_tag = article_tag.find("time")

                if not title_tag or not link_tag:
                    continue

                title = title_tag.get_text(strip=True)
                raw_href = link_tag["href"]
                if raw_href.startswith("./"):
                    article_url = "https://news.google.com" + raw_href[1:]
                elif raw_href.startswith("http"):
                    article_url = raw_href
                else:
                    continue

                if article_url in seen_urls:
                    continue
                seen_urls.add(article_url)

                source_tag = article_tag.find("div", class_=lambda c: c and "source" in c.lower()) \
                             or article_tag.find("span")
                source = source_tag.get_text(strip=True) if source_tag else "Google News"
                published = time_tag.get("datetime", "") if time_tag else ""

                articles.append({
                    "title": title,
                    "url": article_url,
                    "source": source,
                    "published_at": published,
                    "description": "",
                })
        except Exception as exc:
            print(f"[Google News] Error for '{query}': {exc}")

    print(f"[Google News] Fetched {len(articles)} articles.")
    return articles
