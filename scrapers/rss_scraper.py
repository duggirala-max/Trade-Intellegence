import feedparser


# (source_name, feed_url, source_region)
RSS_FEEDS = [
    # --- India-centric sources ---
    ("Reuters India", "https://feeds.reuters.com/reuters/INtopNews", "India"),
    ("Economic Times Trade", "https://economictimes.indiatimes.com/industry/indl-goods/svs/engineering/rssfeeds/13358575.cms", "India"),
    ("Economic Times Economy", "https://economictimes.indiatimes.com/economy/foreign-trade/rssfeeds/1977021501.cms", "India"),
    ("Hindu BusinessLine", "https://www.thehindubusinessline.com/economy/feeder/default.rss", "India"),
    # --- Global / neutral sources ---
    ("Reuters Business", "https://feeds.reuters.com/reuters/businessNews", "Global"),
    ("BBC Business", "http://feeds.bbci.co.uk/news/business/rss.xml", "Global"),
    ("FT World", "https://www.ft.com/rss/home/international", "Global"),
    # --- EU / German sources ---
    ("Deutsche Welle Business", "https://rss.dw.com/rdf/rss-en-bus", "EU"),
    ("EurActiv Trade", "https://www.euractiv.com/sections/trade-society/feed/", "EU"),
    ("EurActiv Economics", "https://www.euractiv.com/sections/economics/feed/", "EU"),
    ("Handelsblatt", "https://www.handelsblatt.com/contentexport/feed/top-themen", "EU"),
    ("Spiegel Wirtschaft", "https://www.spiegel.de/wirtschaft/index.rss", "EU"),
    ("Euronews Business", "https://www.euronews.com/rss?level=theme&name=business", "EU"),
]

TRADE_KEYWORDS = [
    # English
    "india", "europe", "eu", "european union", "trade", "export", "import",
    "tariff", "fta", "free trade", "bilateral", "commerce", "supply chain",
    "investment", "customs", "duty", "sanction", "agreement", "asia", "germany",
    # German
    "indien", "asien", "handel", "zoll", "freihandel", "wirtschaft", "investition",
]


def _is_relevant(title: str, description: str, source_region: str) -> bool:
    combined = (title + " " + description).lower()
    hits = sum(1 for kw in TRADE_KEYWORDS if kw in combined)
    # EU/German sources: lower threshold — even 1 keyword passes
    if source_region == "EU":
        return hits >= 1
    return hits >= 2


def fetch_articles() -> list[dict]:
    seen_urls = set()
    articles = []

    for source_name, feed_url, source_region in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries:
                url = entry.get("link", "")
                title = entry.get("title", "")
                description = entry.get("summary", "") or ""
                published = entry.get("published", "") or entry.get("updated", "") or ""

                if not url or url in seen_urls:
                    continue
                if not _is_relevant(title, description, source_region):
                    continue

                seen_urls.add(url)
                articles.append({
                    "title": title,
                    "url": url,
                    "source": source_name,
                    "source_region": source_region,
                    "published_at": published,
                    "description": description[:500],
                })
        except Exception as exc:
            print(f"[RSS] Error fetching '{source_name}': {exc}")

    print(f"[RSS] Fetched {len(articles)} relevant articles.")
    return articles
