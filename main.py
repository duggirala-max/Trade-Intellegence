import os
from dotenv import load_dotenv

load_dotenv()

from scrapers import newsapi_scraper, rss_scraper, google_news_scraper
from ai import grok_analyzer
from email_sender import send_digest

TOP_N = 10


def _deduplicate(articles: list[dict]) -> list[dict]:
    seen_urls: set[str] = set()
    seen_titles: set[str] = set()
    unique = []
    for a in articles:
        url = a.get("url", "").strip()
        title = a.get("title", "").strip().lower()[:80]
        if url and url in seen_urls:
            continue
        if title and title in seen_titles:
            continue
        if url:
            seen_urls.add(url)
        if title:
            seen_titles.add(title)
        unique.append(a)
    return unique


def run() -> None:
    print("=" * 60)
    print("Trade Intelligence Pipeline — Starting")
    print("=" * 60)

    # 1. Collect
    print("\n[Step 1] Collecting articles from all sources...")
    all_articles: list[dict] = []
    all_articles += newsapi_scraper.fetch_articles()
    all_articles += rss_scraper.fetch_articles()
    all_articles += google_news_scraper.fetch_articles()
    all_articles += grok_analyzer.fetch_live_news()
    print(f"\nTotal collected (before dedup): {len(all_articles)}")

    # 2. Deduplicate
    print("\n[Step 2] Deduplicating...")
    unique_articles = _deduplicate(all_articles)
    print(f"After dedup: {len(unique_articles)} articles")

    if not unique_articles:
        print("No articles found. Exiting.")
        return

    # 3. Score
    print(f"\n[Step 3] Scoring {len(unique_articles)} articles with Grok AI...")
    scored_articles = grok_analyzer.score_all(unique_articles)

    # 4. Rank and filter
    print(f"\n[Step 4] Ranking by composite score, keeping top {TOP_N}...")
    ranked = sorted(scored_articles, key=lambda x: x.get("composite_score", 0), reverse=True)
    top_articles = ranked[:TOP_N]

    print("\nTop articles:")
    for i, a in enumerate(top_articles, 1):
        print(f"  {i}. [{a.get('composite_score',0):>4}] {a.get('title','')[:70]}")

    # 5. Executive summary
    print("\n[Step 5] Generating executive summary...")
    executive_summary = grok_analyzer.generate_executive_summary(top_articles)
    if executive_summary:
        print("\nExecutive Summary:\n" + executive_summary)

    # 6. Send
    print("\n[Step 6] Sending email digest with PDF attachment...")
    send_digest(top_articles, executive_summary)

    print("\n[Done] Pipeline completed successfully.")


if __name__ == "__main__":
    run()
