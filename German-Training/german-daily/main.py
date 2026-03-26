# ─────────────────────────────────────────
# Duggirala
# German Daily Learning System
# ─────────────────────────────────────────

import json
import os
import random
import subprocess
import sys
import datetime

import pytz
import google.generativeai as genai

from word_bank import WORDS, LEVELS
from video_seeds import VIDEOS_BY_LEVEL
import pdf_builder
import email_sender

WORDS_PER_DAY = 20
TOTAL_WORDS = 2500
TOTAL_DAYS = 125

# Shuffle WORDS (and LEVELS together) once with a fixed seed so every run
# sees the same ordering, but each 20-word slice spans multiple categories.
_SHUFFLE_SEED = 42
_indices = list(range(TOTAL_WORDS))
random.Random(_SHUFFLE_SEED).shuffle(_indices)
SHUFFLED_WORDS = [WORDS[i] for i in _indices]
SHUFFLED_LEVELS = [LEVELS[i] for i in _indices]


def _load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _atomic_write(path: str, data: dict) -> None:
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def main():
    TEST_MODE = os.environ.get("TEST_MODE", "") == "true"

    # ── STEP 1: GUARDS ──────────────────────────────────────────────────
    if TEST_MODE:
        print("TEST MODE: skipping guards, using fixed word slice 0-20.")
        start, end = 0, WORDS_PER_DAY
        today_words = SHUFFLED_WORDS[start:end]
        today_levels = SHUFFLED_LEVELS[start:end]
        level_label = today_levels[0]
        today_video = VIDEOS_BY_LEVEL[level_label][0]
        day_number = 0  # sentinel: not a real day
    else:
        progress = _load_json("progress.json")

        if progress.get("completed"):
            print(f"Kurs abgeschlossen! Tag {TOTAL_DAYS} wurde bereits gesendet.")
            sys.exit(0)

        berlin = pytz.timezone("Europe/Berlin")
        now = datetime.datetime.now(berlin)

        if now.weekday() >= 5:          # Saturday=5, Sunday=6
            print(f"Heute ist Wochenende ({now.strftime('%A')}). Kein Versand.")
            sys.exit(0)

        today_str = now.strftime("%Y-%m-%d")
        if progress.get("last_sent_date") == today_str:
            print(f"Heute ({today_str}) wurde bereits gesendet.")
            sys.exit(0)

        # ── STEP 2: SLICE + DEDUP ────────────────────────────────────────────
        start = progress["next_word_index"]
        end = start + WORDS_PER_DAY
        today_words = SHUFFLED_WORDS[start:end]
        today_levels = SHUFFLED_LEVELS[start:end]
        level_label = today_levels[0]
        level_videos = VIDEOS_BY_LEVEL[level_label]
        today_video = level_videos[progress["next_video_index"] % len(level_videos)]
        day_number = progress["days_completed"] + 1

    last_sent_path = "last_sent_words.json"
    previous = _load_json(last_sent_path)
    if "words" in previous:
        overlap = set(today_words) & set(previous["words"])
        if overlap:
            print(f"DUPLICATE DETECTED: {overlap}")
            sys.exit(1)
        print("Dedup check passed.")

    if os.path.exists(last_sent_path):
        os.remove(last_sent_path)

    _atomic_write(last_sent_path, {
        "date": today_str,
        "day_number": day_number,
        "word_index_start": start,
        "word_index_end": end,
        "words": today_words,
    })

    # ── STEP 3: GEMINI API ────────────────────────────────────────────────
    api_key = os.environ.get("GEMINI_API_KEY", "")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")

    system_instruction = (
        "Expert German teacher A1–B1. Respond valid JSON only. "
        "No markdown, backticks, or preamble."
    )
    prompt = (
        f"Lessons for {WORDS_PER_DAY} words at ~{level_label} level.\n"
        f"Words: {json.dumps(today_words, ensure_ascii=False)}\n"
        f"Levels: {json.dumps(today_levels, ensure_ascii=False)}\n"
        f"Return ONLY a JSON array of exactly {WORDS_PER_DAY} objects each with:\n"
        "word, article (der/die/das or null), part_of_speech,\n"
        "pronunciation_guide (phonetic for English speakers),\n"
        "primary_meaning, secondary_meanings (list),\n"
        "example_sentences (list of 5 objects each with german and english keys),\n"
        "synonyms (list of 2 objects each with word, example_german, example_english),\n"
        "memory_tip (vivid mnemonic 2-3 sentences),\n"
        "usage_tip (native usage + register 2 sentences),\n"
        "common_mistake (top English-speaker error 1-2 sentences)"
    )

    def _call_gemini(temperature: float) -> list:
        config = genai.types.GenerationConfig(temperature=temperature)
        response = model.generate_content(
            [{"role": "user", "parts": [f"{system_instruction}\n\n{prompt}"]}],
            generation_config=config,
        )
        raw = response.text.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1]
            raw = raw.rsplit("```", 1)[0]
        return json.loads(raw)

    word_data = None
    for temp in [0.7, 0.0]:
        try:
            result = _call_gemini(temp)
            if len(result) == WORDS_PER_DAY:
                word_data = result
                break
            print(f"Gemini returned {len(result)} items, expected {WORDS_PER_DAY}. Retrying.")
        except Exception as exc:
            print(f"Gemini attempt failed (temp={temp}): {exc}")

    if word_data is None:
        print("Both Gemini attempts failed. Using minimal fallback data.")
        word_data = [
            {"word": w, "article": None, "part_of_speech": "unknown",
             "pronunciation_guide": w, "primary_meaning": "See dictionary",
             "secondary_meanings": [], "example_sentences": [],
             "synonyms": [], "memory_tip": "", "usage_tip": "",
             "common_mistake": ""}
            for w in today_words
        ]

    # ── STEP 4: BUILD PDF ────────────────────────────────────────────────
    new_total = progress["total_words_sent"] + WORDS_PER_DAY
    pdf_bytes = pdf_builder.build_pdf(word_data, today_video, day_number, level_label, new_total)

    # ── STEP 5: SEND EMAIL ───────────────────────────────────────────────
    email_sender.send_email(pdf_bytes, day_number, level_label, new_total)

    # ── STEP 6: UPDATE PROGRESS ──────────────────────────────────────────
    _atomic_write("progress.json", {
        "next_word_index": end,
        "next_video_index": progress["next_video_index"] + 1,
        "days_completed": day_number,
        "total_words_sent": new_total,
        "last_sent_date": today_str,
        "completed": end >= TOTAL_WORDS,
    })

    # ── STEP 7: GIT COMMIT ───────────────────────────────────────────────
    try:
        subprocess.run(
            ["git", "config", "user.email", "github-actions[bot]@users.noreply.github.com"],
            check=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "GitHub Actions Bot"],
            check=True,
        )
        subprocess.run(["git", "add", "progress.json", "last_sent_words.json"], check=True)
        subprocess.run(
            ["git", "commit", "-m",
             f"Day {day_number}/{TOTAL_DAYS}: words {start}\u2013{end} \u2713"],
            check=True,
        )
        subprocess.run(["git", "push"], check=True)
    except Exception as exc:
        print(f"Git commit/push failed (non-fatal): {exc}")

    print(f"Tag {day_number}/{TOTAL_DAYS} erfolgreich gesendet. "
          f"Wörter {start}–{end}. Gesamt: {new_total}/{TOTAL_WORDS}.")


if __name__ == "__main__":
    main()
