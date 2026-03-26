# ─────────────────────────────────────────
# Duggirala
# German Daily Learning System
# ─────────────────────────────────────────

import os
import smtplib
import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

import pytz

WEEKDAYS = {0: "Montag", 1: "Dienstag", 2: "Mittwoch", 3: "Donnerstag",
            4: "Freitag", 5: "Samstag", 6: "Sonntag"}
MONTHS = {1: "Januar", 2: "Februar", 3: "März", 4: "April", 5: "Mai",
          6: "Juni", 7: "Juli", 8: "August", 9: "September",
          10: "Oktober", 11: "November", 12: "Dezember"}


def send_email(pdf_bytes: bytes, day_number: int, level_label: str,
               total_words: int) -> None:
    sender = os.environ["SENDER_EMAIL"]
    password = os.environ["SENDER_APP_PASS"]
    recipient = os.environ["RECIPIENT_EMAIL"]

    berlin = pytz.timezone("Europe/Berlin")
    now = datetime.datetime.now(berlin)
    weekday_name = WEEKDAYS[now.weekday()]
    month_name = MONTHS[now.month]

    subject = (
        f"🇩🇪 Tag {day_number}/125 | {level_label} | Dein Deutsch — "
        f"{weekday_name}, {now.day}. {month_name} {now.year}"
    )

    progress_pct = round(total_words / 2500 * 100, 1)

    body = f"""Guten Morgen! ☀️

Dein tägliches Deutsch-Paket ist da.

📚 Heute: 20 neue Wörter auf {level_label}-Niveau
📅 Tag {day_number} von 125 (~6 Monate bis B1)
🎯 Gelernt: {total_words} von 2.500 Wörtern
📊 Fortschritt: {progress_pct}%

Was dich heute erwartet:
  • 20 Wörter mit Artikel, Aussprache und Bedeutung
  • 5 Beispielsätze pro Wort (Deutsch + Englisch)
  • 2 Synonyme pro Wort mit Beispielen
  • Merkhilfe, Verwendungstipp und häufiger Fehler
  • Tagesübersicht aller 20 Wörter auf der letzten Seite
  • Hörübung: Ein kurzes YouTube-Video
  • Profi-Tipp des Tages

Viel Erfolg! 💪

---
Automatisch gesendet. Tag {day_number}/125 abgeschlossen.
"""

    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))

    attachment = MIMEApplication(pdf_bytes, _subtype="pdf")
    filename = f"Deutsch_Tag_{day_number:03d}_{level_label}.pdf"
    attachment.add_header("Content-Disposition", "attachment", filename=filename)
    msg.attach(attachment)

    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        smtp.starttls()
        smtp.login(sender, password)
        smtp.send_message(msg)
