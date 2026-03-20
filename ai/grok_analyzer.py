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
  "monetisation": "<Concrete zero/low-capital, brain-work monetisation plan (4-6 sentences). Specify: (1) what role to play (consultant, broker, researcher, advisor, matchmaker, etc.), (2) which specific Indian or European businesses to approach, (3) what exactly to offer them, (4) how to charge (retainer, success fee, per-project), (5) the single first step to take today with no money. Do NOT suggest buying inventory, importing goods yourself, or any capital-intensive action.>",
  "action_plan": "<Numbered list of exactly 3-5 concrete steps to take TODAY or THIS WEEK. Step 1 must be free and doable in under 30 minutes (e.g. send a cold LinkedIn message, draft a 1-page pitch, search a specific supplier directory). Name real platforms (LinkedIn, Kompass, Alibaba, Germany Trade & Invest, GTAI, Make in India portal), real business types, and real documents. No vague advice — each step must be specific enough to act on immediately.>"
}}

Scoring guide:
- relevance_score: How directly relevant to Germany/EU ↔ India trade flows, tariffs, policy, or investment?
- credibility_score: How credible is the reporting? (10 = Reuters/FT/DW, 1 = unknown blog)
- opportunity_score: How actionable is this for a Germany-based individual with no capital, in the next 1-6 months?

If the article is NOT relevant to India-Germany/EU trade (e.g. domestic Indian stocks, unrelated finance, Middle East conflict without trade angle), set relevance_score to 1 and opportunity_score to 1.

Article title: {title}
Source: {source}
Description: {description}
URL: {url}

Return ONLY the JSON object, no markdown fences, no explanation."""


EXEC_SUMMARY_PROMPT = """You are a senior trade intelligence analyst writing a daily briefing for a Germany-based trade entrepreneur with no startup capital.

Below are today's top {n} India–Germany/EU trade intelligence articles (titles and opportunity notes only).

Write a concise executive briefing in plain text with exactly this structure:
1. Two sentences summarising today's overall India-Germany trade landscape.
2. Between 3 and 5 bullet points (use "• " prefix). Each bullet names ONE specific opportunity and ONE concrete first action.
3. One final line starting with "TOP ACTION TODAY: " — the single most important thing to do right now, specific and free.

Articles:
{articles_text}

Rules: plain text only, no markdown headers, no asterisks, no bold tags."""


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


def generate_executive_summary(articles: list[dict]) -> str:
    if not os.environ.get("GROK_API_KEY", ""):
        return ""
    client = _client()
    articles_text = "\n".join(
        f"- {a.get('title', '')} | {a.get('opportunity_note', a.get('description', ''))[:150]}"
        for a in articles
    )
    prompt = EXEC_SUMMARY_PROMPT.format(n=len(articles), articles_text=articles_text)
    try:
        resp = client.chat.completions.create(
            model=GROK_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
        summary = resp.choices[0].message.content.strip()
        print(f"[Grok Exec] Executive summary generated ({len(summary)} chars).")
        return summary
    except Exception as exc:
        print(f"[Grok Exec] Error generating executive summary: {exc}")
        return ""
