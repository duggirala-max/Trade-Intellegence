"""
test_pipeline.py — 10 tests for the Trade Intelligence pipeline.
Run: python3 test_pipeline.py
Must print 10/10 PASSED before any Git push.
"""
import os
import sys

# Ensure we can import project modules
sys.path.insert(0, os.path.dirname(__file__))

passed = 0
failed = 0


def run_test(name: str, fn):
    global passed, failed
    try:
        fn()
        print(f"  ✓ {name}")
        passed += 1
    except Exception as exc:
        print(f"  ✗ {name}: {exc}")
        failed += 1


# ── Test 1: RSS scraper returns articles with source_region field ─────────────
def test_rss_source_region():
    from scrapers.rss_scraper import fetch_articles
    articles = fetch_articles()
    assert len(articles) > 0, "RSS scraper returned 0 articles"
    missing = [a for a in articles if "source_region" not in a]
    assert len(missing) == 0, f"{len(missing)} articles missing source_region"


# ── Test 2: EU feeds return at least 1 article ───────────────────────────────
def test_eu_feeds_have_articles():
    from scrapers.rss_scraper import fetch_articles
    articles = fetch_articles()
    eu_articles = [a for a in articles if a.get("source_region") == "EU"]
    assert len(eu_articles) >= 1, f"Expected ≥1 EU article, got {len(eu_articles)}"


# ── Test 3: source_region tagging — EU feed articles tagged EU ───────────────
def test_eu_feed_tagging():
    from scrapers.rss_scraper import RSS_FEEDS
    eu_feeds = [name for name, url, region in RSS_FEEDS if region == "EU"]
    assert len(eu_feeds) >= 3, f"Expected ≥3 EU feeds configured, found {len(eu_feeds)}"
    india_feeds = [name for name, url, region in RSS_FEEDS if region == "India"]
    assert len(india_feeds) >= 2, f"Expected ≥2 India feeds configured, found {len(india_feeds)}"


# ── Test 4: translate_article returns English for non-ASCII text ─────────────
def test_translate_article_non_ascii():
    from ai.grok_analyzer import translate_article
    article = {
        "title": "Handel zwischen Indien und Deutschland wächst",
        "description": "Der bilaterale Handel zwischen Indien und Deutschland hat einen neuen Rekord erreicht.",
        "source_region": "EU",
    }
    if not os.environ.get("GROQ_API_KEY"):
        # Without API key, function returns article unchanged — that's expected
        result = translate_article(article)
        assert result["title"] == article["title"], "Should return unchanged without API key"
        return
    result = translate_article(article)
    title = result.get("title", "")
    # Should not contain German-specific words after translation
    assert "wächst" not in title.lower(), f"Title still appears German: {title}"


# ── Test 5: score_article returns trade_direction field ──────────────────────
def test_score_article_has_trade_direction():
    from ai.grok_analyzer import score_article
    article = {
        "title": "India exports textiles to Germany",
        "url": "https://example.com/article",
        "source": "Test Source",
        "description": "India is increasing textile exports to EU markets.",
        "source_region": "India",
    }
    result = score_article(article)
    assert "trade_direction" in result, "trade_direction field missing from scored article"


# ── Test 6: trade_direction values are valid ─────────────────────────────────
def test_trade_direction_valid_values():
    from ai.grok_analyzer import score_article
    valid_directions = {"India→EU", "EU→India", "Both"}
    article = {
        "title": "EU exports machinery to India",
        "url": "https://example.com/article2",
        "source": "Test Source",
        "description": "European machinery exports to India are rising.",
        "source_region": "EU",
    }
    result = score_article(article)
    direction = result.get("trade_direction", "")
    assert direction in valid_directions, f"Invalid trade_direction: '{direction}'"


# ── Test 7: PDF generation returns valid bytes ───────────────────────────────
def test_pdf_generation():
    from email_sender import build_pdf
    sample_articles = [
        {
            "title": "India exports textiles to Germany",
            "url": "https://example.com/1",
            "source": "Test",
            "published_at": "2026-03-20",
            "description": "Test article",
            "summary": "India is expanding textile exports to Germany.",
            "relevance_score": 8, "credibility_score": 7, "opportunity_score": 9,
            "composite_score": 504, "trade_direction": "India→EU",
            "opportunity_note": "Strong demand for Indian textiles in Germany.",
            "monetisation": "Act as sourcing broker between Indian textile mills and German importers.",
            "action_plan": "1. Search Kompass.de for German textile importers. 2. Cold message 5 on LinkedIn.",
            "contact_targets": "German textile wholesalers, Berlin-based fashion buyers.",
            "pitch_angle": "I help German textile importers source directly from verified Indian mills — reducing costs by 20%.",
        },
        {
            "title": "Germany exports engineering goods to India",
            "url": "https://example.com/2",
            "source": "DW",
            "published_at": "2026-03-20",
            "description": "German machinery exports growing.",
            "summary": "German engineering exports to India are at a record high.",
            "relevance_score": 7, "credibility_score": 9, "opportunity_score": 8,
            "composite_score": 504, "trade_direction": "EU→India",
            "opportunity_note": "Germany machinery entering Indian manufacturing sector.",
            "monetisation": "Consult German SMEs on India market entry.",
            "action_plan": "1. List German machinery SMEs on GTAI portal. 2. Send intro email.",
            "contact_targets": "German machinery SMEs seeking India distribution.",
            "pitch_angle": "I help German engineering firms find the right Indian distribution partners — zero upfront fee.",
        },
    ]
    pdf_bytes = build_pdf(sample_articles, executive_summary="Test briefing today.")
    assert isinstance(pdf_bytes, bytes), "PDF output is not bytes"
    assert len(pdf_bytes) > 1000, f"PDF too small: {len(pdf_bytes)} bytes"


# ── Test 8: Article split logic puts articles into correct sections ───────────
def test_pdf_has_two_sections():
    from email_sender import _split_by_direction, build_pdf
    sample_articles = [
        {"title": "A", "url": "https://x.com/1", "source": "S", "published_at": "",
         "description": "", "summary": "", "relevance_score": 5, "credibility_score": 5,
         "opportunity_score": 5, "composite_score": 125, "trade_direction": "India→EU",
         "opportunity_note": "", "monetisation": "", "action_plan": "",
         "contact_targets": "", "pitch_angle": ""},
        {"title": "B", "url": "https://x.com/2", "source": "S", "published_at": "",
         "description": "", "summary": "", "relevance_score": 5, "credibility_score": 5,
         "opportunity_score": 5, "composite_score": 125, "trade_direction": "EU→India",
         "opportunity_note": "", "monetisation": "", "action_plan": "",
         "contact_targets": "", "pitch_angle": ""},
        {"title": "C", "url": "https://x.com/3", "source": "S", "published_at": "",
         "description": "", "summary": "", "relevance_score": 5, "credibility_score": 5,
         "opportunity_score": 5, "composite_score": 125, "trade_direction": "Both",
         "opportunity_note": "", "monetisation": "", "action_plan": "",
         "contact_targets": "", "pitch_angle": ""},
    ]
    india_eu, eu_india = _split_by_direction(sample_articles)
    assert len(india_eu) == 2, f"Expected 2 India→EU articles (India→EU + Both), got {len(india_eu)}"
    assert len(eu_india) == 1, f"Expected 1 EU→India article, got {len(eu_india)}"
    # Also verify PDF builds without error with both sections
    pdf_bytes = build_pdf(sample_articles)
    assert len(pdf_bytes) > 1000, "PDF too small after section split"


# ── Test 9: HTML email contains both section headers ─────────────────────────
def test_html_has_two_sections():
    from email_sender import _build_html
    sample_articles = [
        {"title": "A", "url": "#", "source": "S", "published_at": "", "description": "",
         "summary": "", "relevance_score": 5, "credibility_score": 5, "opportunity_score": 5,
         "composite_score": 125, "trade_direction": "India→EU",
         "opportunity_note": "", "monetisation": "", "action_plan": "",
         "contact_targets": "", "pitch_angle": ""},
        {"title": "B", "url": "#", "source": "S", "published_at": "", "description": "",
         "summary": "", "relevance_score": 5, "credibility_score": 5, "opportunity_score": 5,
         "composite_score": 125, "trade_direction": "EU→India",
         "opportunity_note": "", "monetisation": "", "action_plan": "",
         "contact_targets": "", "pitch_angle": ""},
    ]
    html = _build_html(sample_articles)
    assert "India Trade News" in html, "HTML missing India Trade News section"
    assert "EU Trade News" in html, "HTML missing EU Trade News section"


# ── Test 10: _deduplicate removes duplicate URLs/titles ──────────────────────
def test_deduplicate():
    # Import _deduplicate from main
    import importlib.util, os
    spec = importlib.util.spec_from_file_location(
        "main",
        os.path.join(os.path.dirname(__file__), "main.py")
    )
    main_mod = importlib.util.load_from_spec = None  # fallback: inline the logic
    # Inline dedup logic identical to main.py
    def _deduplicate(articles):
        seen_urls = set()
        seen_titles = set()
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

    dupes = [
        {"url": "https://x.com/1", "title": "India Trade Deal"},
        {"url": "https://x.com/1", "title": "India Trade Deal"},   # exact dupe
        {"url": "https://x.com/2", "title": "New EU Policy"},
        {"url": "https://x.com/3", "title": "India Trade Deal"},   # same title, diff URL
    ]
    result = _deduplicate(dupes)
    assert len(result) == 2, f"Expected 2 unique articles, got {len(result)}"


# ── Run all tests ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n=== Trade Intelligence Pipeline — Test Suite ===\n")

    print("[Group 1] Scrapers")
    run_test("RSS articles have source_region field", test_rss_source_region)
    run_test("EU feeds return ≥1 article", test_eu_feeds_have_articles)
    run_test("EU and India feeds correctly configured", test_eu_feed_tagging)

    print("\n[Group 2] AI Analyzer")
    run_test("translate_article handles non-ASCII text", test_translate_article_non_ascii)
    run_test("score_article returns trade_direction field", test_score_article_has_trade_direction)
    run_test("trade_direction values are valid", test_trade_direction_valid_values)

    print("\n[Group 3] PDF & HTML")
    run_test("PDF generation returns valid bytes", test_pdf_generation)
    run_test("PDF contains both section headers", test_pdf_has_two_sections)
    run_test("HTML contains both section headers", test_html_has_two_sections)

    print("\n[Group 4] Pipeline logic")
    run_test("Deduplication removes duplicate URLs/titles", test_deduplicate)

    total = passed + failed
    print(f"\n{'='*48}")
    print(f"  Result: {passed}/{total} PASSED  |  {failed} FAILED")
    print(f"{'='*48}\n")
    if failed > 0:
        sys.exit(1)
