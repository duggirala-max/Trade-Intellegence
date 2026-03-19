import feedparser


RSS_FEEDS = [
    # Reuters
    ("Reuters Business", "https://feeds.reuters.com/reuters/businessNews"),
    ("Reuters India", "https://feeds.reuters.com/reuters/INtopNews"),
    # BBC
    ("BBC Business", "http://feeds.bbci.co.uk/news/business/rss.xml"),
    # Economic Times
    ("Economic Times Trade", "https://economictimes.indiatimes.com/industry/indl-goods/svs/engineering/rssfeeds/13358575.cms"),
    ("Economic Times Economy", "https://economictimes.indiatimes.com/economy/foreign-trade/rssfeeds/1977021501.cms"),
    # Hindu BusinessLine
    ("Hindu BusinessLine", "https://www.thehindubusinessline.com/economy/feeder/default.rss"),
    # Euronews
    ("Euronews Business", "https://www.euronews.com/rss?level=theme&name=business"),
    # Financial Times (free RSS)
    ("FT World", "https://www.ft.com/rss/home/international"),
]

TRADE_KEYWORDS = [
    "india", "europe", "eu", "european union", "trade", "export", "import",
    "tariff", "fta", "free trade", "bilateral", "commerce", "supply chain",
    "investment", "customs", "duty", "sanction", "agreement",
]


def _is_relevant(title: str, description: str) -> bool:
    combined = (title + " " + description).lower()
    hits = sum(1 for kw in TRADE_KEYWORDS if kw in combined)
    return hits >= 2


def fetch_articles() -> list[dict]:
    seen_urls = set()
    articles = []

    for source_name, feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries:
                url = entry.get("link", "")
                title = entry.get("title", "")
                description = entry.get("summary", "") or ""
                published = entry.get("published", "") or entry.get("updated", "") or ""

                if not url or url in seen_urls:
                    continue
                if not _is_relevant(title, description):
                    continue

                seen_urls.add(url)
                articles.append({
                    "title": title,
                    "url": url,
                    "source": source_name,
                    "published_at": published,
                    "description": description[:500],
                })
        except Exception as exc:
            print(f"[RSS] Error fetching '{source_name}': {exc}")

    print(f"[RSS] Fetched {len(articles)} relevant articles.")
    return articles
