# 🇩🇪 German Daily — A1 to B1 in 6 Months

## What This Does

20 words/day × 125 weekdays = 2,500 words. One richly formatted PDF email at 7am CET every weekday. Fully automated after one git push. Self-stops at day 125.

Each daily PDF includes:
- 20 words with article, pronunciation guide, and primary + secondary meanings
- 5 example sentences per word (German **and** English translation)
- 2 synonyms per word with usage examples
- Memory tip, usage tip, and common mistake for each word
- **Daily summary table**: all 20 words at a glance (German → English)
- A YouTube listening exercise (2–6 min video)
- A daily pro learning tip (125 unique tips, day 1 through 125)

---

## Learning Journey

| Phase | Days | Words | Level |
|-------|------|-------|-------|
| 1 | 1–25 | 1–500 | A1 |
| 2 | 26–50 | 501–1,000 | A2 |
| 3 | 51–125 | 1,001–2,500 | B1 |

Each day's 20 words are drawn from a shuffled mix of all word categories — you'll never get 20 family words or 20 numbers in a single day. The shuffle is deterministic, so the order is always the same across runs.

---

## One-Time Setup (10 minutes)

### Step 1 — Clone repo

```bash
git clone https://github.com/duggirala-max/German-Training
cd German-Training/german-daily
```

### Step 2 — Gemini API key (free)

1. Go to [aistudio.google.com](https://aistudio.google.com)
2. Click **Get API Key** → **Create API key**
3. Copy the key

Free tier: 1,500 requests/day. You use 1 per weekday.

### Step 3 — Gmail App Password

1. [myaccount.google.com](https://myaccount.google.com) → Security
2. Enable 2-Step Verification if not already on
3. Search for **App passwords** → Mail → Generate
4. Copy the 16-character code (no spaces)

### Step 4 — Add 4 GitHub Secrets

Go to: **Repo → Settings → Secrets and variables → Actions → New repository secret**

| Secret name | Value |
|-------------|-------|
| `GEMINI_API_KEY` | Key from aistudio.google.com |
| `SENDER_EMAIL` | yourgmail@gmail.com |
| `SENDER_APP_PASS` | 16-char app password (no spaces) |
| `RECIPIENT_EMAIL` | Email to receive the daily lessons |

### Step 5 — Test immediately

**Actions → Daily German Lesson → Run workflow → Run workflow**

Check your inbox within 3 minutes.

### Step 6 — Done. Never touch it again.

The bot runs every weekday at 7am CET, commits progress to the repo, and stops automatically on day 125.

---

## How Duplication Is Prevented (3 layers)

1. **`last_sent_date`** — blocks same-day re-runs (the workflow fires twice at 5am and 6am UTC for summer/winter time; the second run is silently skipped)
2. **`next_word_index`** — advances sequentially, never goes backward
3. **`last_sent_words.json`** — explicit word-level cross-check before every send; hard `exit(1)` if any overlap is detected

---

## The Bot's Daily Routine (you are never involved)

```
7am CET: GitHub wakes the bot
→ Load progress.json (check if completed, check day of week, check if already sent today)
→ Dedup check against last_sent_words.json
→ Single Gemini API call (generates all 20 word lessons in one request)
→ Build PDF with fpdf2 (lesson content + daily summary + video + pro tip)
→ Send email via Gmail SMTP with PDF attached
→ Update progress.json (advance index, increment counter)
→ Bot commits progress.json + last_sent_words.json back to repo
→ Sleep until tomorrow
```

---

## SaaS Future

See `SAAS_ROADMAP.docx` for the complete technical blueprint to scale this into a multi-user paid platform with Stripe subscriptions, Supabase database, per-user scheduling via Trigger.dev, and a Next.js dashboard.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| No email | Check spam folder; check Actions tab for red ✗ |
| Action fails | Click the failed run → read the logs |
| Duplicate cron trigger | Berlin timezone guard in `main.py` silently skips the second run |
| Want to reset | Edit `progress.json`: set `next_word_index=0`, `days_completed=0`, `completed=false`; delete `last_sent_words.json`; commit and push |
| SMTP error | Verify `SENDER_APP_PASS` has no spaces and 2FA is enabled on Gmail |
| Gemini error | Verify `GEMINI_API_KEY` is valid; check free-tier quota at aistudio.google.com |
