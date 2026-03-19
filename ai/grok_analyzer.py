import os
import json
from openai import OpenAI


GROK_BASE_URL = "https://api.x.ai/v1"
GROK_MODEL = "grok-3-mini"

LIVE_SEARCH_QUERIES = [
    "India Germany trade news today",
    "India EU import Germany latest",
    "Germany import India export opportunity this week",
    "India European Union FTA tariff update",
]

SCORE_PROMPT = """You are a senior trade intelligence analyst. The reader is based in Germany and is looking for:
1. Opportunities to IMPORT products from India into Germany/EU.
2. Opportunities to EXPORT products or services from Germany/EU to India.

The reader has NO startup capital — they want ZERO or LOW capital ideas that rely on brain work, connections, and expertise:
examples: sourcing broker, trade consultant, matchmaking service, export documentation advisor, market-entry researcher, freelance compliance checker, digital intermediary.

Analyse the news article below and return ONLY a valid JSON object with these exact keys:
{{
  "relevance_score": <integer 1-10>,
  "credibility_score": <integer 1-10>,
  "opportunity_score": <integer 1-10>,
  "summary": "<2-3 sentence factual summary>",
  "opportunity_note": "<1-2 sentences: what trade direction this opens — import to Germany, export to India, or both>",
  "monetisation": "<Concrete zero/low-capital, brain-work monetisation plan (4-6 sentences). Specify: (1) what role to play (consultant, broker, researcher, advisor, matchmaker, etc.), (2) which specific Indian or European businesses to approach, (3) what exactly to offer them, (4) how to charge (retainer, success fee, per-project), (5) the single first step to take today with no money. Do NOT suggest buying inventory, importing goods yourself, or any capital-intensive action.>"
}}

Scoring guide:
- relevance_score: How directly relevant to Germany/EU ↔ India trade flows, tariffs, policy, or investment?
- credibility_score: How credible is the reporting? (10 = Reuters/FT/DW, 1 = unknown blog)
- opportunity_score: How actionable is this for a Germany-based individual with no capital, in the next 1-6 months?

Article title: {title}
Source: {source}
Description: {description}
URL: {url}

Return ONLY the JSON object, no markdown fences, no explanation."""


def _client() -> OpenAI:
    api_key = os.environ.get("GROK_API_KEY", "")
    if not api_key:
        raise ValueError("GROK_API_KEY is not set.")
    return OpenAI(api_key=api_key, base_url=GROK_BASE_URL)


def fetch_live_news() -> list[dict]:
    if not os.environ.get("GROK_API_KEY", ""):
        print("[Grok Live] GROK_API_KEY not set — skipping.")
        return []
    client = _client()
    seen_titles: set[str] = set()
    articles = []

    for query in LIVE_SEARCH_QUERIES:
        try:
            resp = client.chat.completions.create(
                model=GROK_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a real-time news retrieval assistant. "
                            "Search the web for the latest news on the given topic and return "
                            "a JSON array of up to 5 articles. Each article must have: "
                            "title, url, source, published_at, description. "
                            "Return ONLY the JSON array, no markdown."
                        ),
                    },
                    {"role": "user", "content": f"Find the latest news: {query}"},
                ],
            )
            raw = resp.choices[0].message.content.strip()
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            items = json.loads(raw)
            for item in items:
                title = item.get("title", "")
                if title and title not in seen_titles:
                    seen_titles.add(title)
                    articles.append({
                        "title": title,
                        "url": item.get("url", ""),
                        "source": item.get("source", "Grok Live"),
                        "published_at": item.get("published_at", ""),
                        "description": item.get("description", ""),
                    })
        except Exception as exc:
            print(f"[Grok Live] Error for '{query}': {exc}")

    print(f"[Grok Live] Fetched {len(articles)} live articles.")
    return articles


def score_article(article: dict) -> dict:
    if not os.environ.get("GROK_API_KEY", ""):
        article.update({"relevance_score": 5, "credibility_score": 5, "opportunity_score": 5,
                        "composite_score": 125, "summary": article.get("description", ""),
                        "opportunity_note": "N/A — GROK_API_KEY not set.",
                        "monetisation": "N/A — GROK_API_KEY not set."})
        return article
    client = _client()
    prompt = SCORE_PROMPT.format(
        title=article.get("title", ""),
        source=article.get("source", ""),
        description=article.get("description", "")[:800],
        url=article.get("url", ""),
    )
    try:
        resp = client.chat.completions.create(
            model=GROK_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = resp.choices[0].message.content.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        scores = json.loads(raw)
        article.update(scores)
        article["composite_score"] = (
            scores.get("relevance_score", 0)
            * scores.get("credibility_score", 0)
            * scores.get("opportunity_score", 0)
        )
    except Exception as exc:
        print(f"[Grok Score] Error scoring '{article.get('title', '')}': {exc}")
        article.update({
            "relevance_score": 0,
            "credibility_score": 0,
            "opportunity_score": 0,
            "composite_score": 0,
            "summary": article.get("description", ""),
            "opportunity_note": "",
            "monetisation": "",
        })
    return article


def score_all(articles: list[dict]) -> list[dict]:
    scored = []
    for i, article in enumerate(articles):
        print(f"[Grok Score] Scoring {i+1}/{len(articles)}: {article.get('title', '')[:60]}")
        scored.append(score_article(article))
    return scored
