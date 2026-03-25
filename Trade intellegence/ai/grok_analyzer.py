import os
import json
from openai import OpenAI


GROK_BASE_URL = "https://api.groq.com/openai/v1"
GROK_MODEL = "llama-3.3-70b-versatile"

LIVE_SEARCH_QUERIES = [
    "India Germany trade news today",
    "India EU import Germany latest",
    "Germany import India export opportunity this week",
    "India European Union FTA tariff update",
]

SCORE_PROMPT = """You are a senior trade intelligence analyst. The reader is based in Germany and is looking for:
1. Opportunities to IMPORT products from India into Germany/EU.
2. Opportunities to EXPORT products or services from Germany/EU to India or Asia.

The reader has NO startup capital — they want ZERO or LOW capital ideas that rely on brain work, connections, and expertise:
examples: sourcing broker, trade consultant, matchmaking service, export documentation advisor, market-entry researcher, freelance compliance checker, digital intermediary.

If the article is in a language other than English (e.g. German, French, Dutch), translate the title and description to English before scoring. Do not mention the translation in your output.

Analyse the news article below and return ONLY a valid JSON object with these exact keys:
{{
  "relevance_score": 7,
  "credibility_score": 8,
  "opportunity_score": 6,
  "trade_direction": "India→EU",
  "summary": "<2-3 sentence factual summary in English>",
  "opportunity_note": "<1-2 sentences: what trade direction this opens — import to Germany, export to India/Asia, or both>",
  "monetisation": "<Concrete zero/low-capital, brain-work monetisation plan (4-6 sentences). Specify: (1) what role to play (consultant, broker, researcher, advisor, matchmaker, etc.), (2) which specific Indian or European businesses to approach, (3) what exactly to offer them, (4) how to charge (retainer, success fee, per-project), (5) the single first step to take today with no money. Do NOT suggest buying inventory, importing goods yourself, or any capital-intensive action.>",
  "action_plan": "<Numbered list of exactly 3-5 concrete steps to take TODAY or THIS WEEK. Step 1 must be free and doable in under 30 minutes (e.g. send a cold LinkedIn message, draft a 1-page pitch, search a specific supplier directory). Name real platforms (LinkedIn, Kompass, Alibaba, Germany Trade & Invest, GTAI, Make in India portal), real business types, and real documents. No vague advice — each step must be specific enough to act on immediately.>",
  "contact_targets": "<2-3 specific types of companies or organisations to approach first, with their country and a reason why they are the best first contact>",
  "pitch_angle": "<One punchy sentence you could use as the subject line of a cold email or LinkedIn message to open a conversation about this opportunity>"
}}

Replace the example values with your actual scores (integers 1-10) and the correct trade_direction string.
trade_direction MUST be exactly one of these three strings: "India→EU", "EU→India", "Both".
- India→EU: India exporting to Europe / EU importing from India
- EU→India: Germany/EU exporting to India or entering Asian markets
- Both: bidirectional opportunity

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

Below are today's top {n} India–Germany/EU trade intelligence articles, split by trade direction (titles, directions, and opportunity notes).

Write a concise executive briefing in plain text with exactly this structure:
1. Two sentences summarising today's overall India-Germany trade landscape.
2. Between 3 and 5 bullet points (use "• " prefix). Each bullet names ONE specific opportunity, its trade direction (India→EU or EU→India), and ONE concrete first action.
3. One final line starting with "TOP ACTION TODAY: " — the single most important thing to do right now, specific and free.

Articles:
{articles_text}

Rules: plain text only, no markdown headers, no asterisks, no bold tags."""


def _client() -> OpenAI:
    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        raise ValueError("GROQ_API_KEY is not set.")
    return OpenAI(api_key=api_key, base_url=GROK_BASE_URL)


def fetch_live_news() -> list[dict]:
    # Groq models do not support live web search — news sourced from RSS and NewsAPI only.
    print("[AI Live] Skipping live search (not supported by Groq).")
    return []


def translate_article(article: dict) -> dict:
    """Translate title and description to English if non-ASCII characters detected."""
    title = article.get("title", "")
    description = article.get("description", "")
    # Detect non-ASCII (German umlauts, accented chars, etc.)
    has_non_ascii = any(ord(c) > 127 for c in title + description)
    if not has_non_ascii:
        return article
    if not os.environ.get("GROQ_API_KEY", ""):
        return article
    try:
        client = _client()
        prompt = (
            "Translate the following news article fields from their original language to English. "
            "Return ONLY a valid JSON object with keys \"title\" and \"description\".\n\n"
            f"title: {title}\ndescription: {description[:300]}"
        )
        resp = client.chat.completions.create(
            model=GROK_MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )
        data = json.loads(resp.choices[0].message.content.strip())
        article["title"] = data.get("title", title)
        article["description"] = data.get("description", description)
        article["translated"] = True
        print(f"[Translate] Translated: {article['title'][:60]}")
    except Exception as exc:
        print(f"[Translate] Error translating '{title[:40]}': {exc}")
    return article


def score_article(article: dict) -> dict:
    if not os.environ.get("GROQ_API_KEY", ""):
        article.update({"relevance_score": 5, "credibility_score": 5, "opportunity_score": 5,
                        "composite_score": 125, "summary": article.get("description", ""),
                        "opportunity_note": "N/A — GROQ_API_KEY not set.",
                        "monetisation": "N/A — GROQ_API_KEY not set.",
                        "trade_direction": "Both",
                        "contact_targets": "",
                        "pitch_angle": ""})
        return article

    # Translate before scoring if needed
    article = translate_article(article)

    client = _client()
    prompt = SCORE_PROMPT.format(
        title=article.get("title", ""),
        source=article.get("source", ""),
        description=article.get("description", "")[:300],
        url=article.get("url", ""),
    )
    try:
        resp = client.chat.completions.create(
            model=GROK_MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )
        raw = resp.choices[0].message.content.strip()
        scores = json.loads(raw)
        article.update(scores)
        article["composite_score"] = (
            scores.get("relevance_score", 0)
            * scores.get("credibility_score", 0)
            * scores.get("opportunity_score", 0)
        )
        # Normalise trade_direction — AI sometimes returns "Neither" or other values
        valid_directions = {"India→EU", "EU→India", "Both"}
        if article.get("trade_direction") not in valid_directions:
            article["trade_direction"] = "Both"
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
            "trade_direction": "Both",
            "contact_targets": "",
            "pitch_angle": "",
        })
    return article


def score_all(articles: list[dict]) -> list[dict]:
    scored = []
    for i, article in enumerate(articles):
        print(f"[Grok Score] Scoring {i+1}/{len(articles)}: {article.get('title', '')[:60]}")
        scored.append(score_article(article))
    return scored


def generate_executive_summary(articles: list[dict]) -> str:
    if not os.environ.get("GROQ_API_KEY", ""):
        return ""
    client = _client()
    articles_text = "\n".join(
        f"- [{a.get('trade_direction', 'Both')}] {a.get('title', '')} | {a.get('opportunity_note', a.get('description', ''))[:150]}"
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
