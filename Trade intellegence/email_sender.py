import os
import smtplib
import tempfile
from html import escape as _esc
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER


# ── Helpers ──────────────────────────────────────────────────────────────────

def _score_bar(score: int, max_score: int = 10) -> str:
    filled = round(score / max_score * 8)
    return "█" * filled + "░" * (8 - filled) + f"  {score}/10"


def _date_str() -> str:
    return datetime.now(timezone.utc).strftime("%d %B %Y")


def _split_by_direction(articles: list[dict]) -> tuple[list[dict], list[dict]]:
    """Split articles into India→EU and EU→India buckets."""
    india_eu = []
    eu_india = []
    for a in articles:
        direction = a.get("trade_direction", "Both")
        if direction == "EU→India":
            eu_india.append(a)
        else:
            # India→EU and Both go to the India→EU section
            india_eu.append(a)
    return india_eu, eu_india


# ── PDF builder ───────────────────────────────────────────────────────────────

def build_pdf(articles: list[dict], executive_summary: str = "") -> bytes:
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontSize=22,
        textColor=colors.HexColor("#1a3a5c"),
        spaceAfter=4,
        alignment=TA_CENTER,
    )
    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        fontSize=11,
        textColor=colors.HexColor("#555555"),
        alignment=TA_CENTER,
        spaceAfter=20,
    )
    section_header = ParagraphStyle(
        "SectionHeader",
        parent=styles["Heading2"],
        fontSize=13,
        textColor=colors.HexColor("#1a3a5c"),
        spaceBefore=14,
        spaceAfter=4,
    )
    section_banner = ParagraphStyle(
        "SectionBanner",
        parent=styles["Heading1"],
        fontSize=15,
        textColor=colors.white,
        backColor=colors.HexColor("#1a3a5c"),
        spaceBefore=18,
        spaceAfter=8,
        leftIndent=8,
        borderPad=6,
    )
    body = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        spaceAfter=6,
    )
    label = ParagraphStyle(
        "Label",
        parent=styles["Normal"],
        fontSize=9,
        textColor=colors.HexColor("#777777"),
        spaceAfter=2,
    )
    monetise_style = ParagraphStyle(
        "Monetise",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#1a5c2a"),
        backColor=colors.HexColor("#f0faf3"),
        spaceAfter=8,
        leftIndent=8,
        rightIndent=8,
        borderPad=6,
    )
    link_style = ParagraphStyle(
        "Link",
        parent=styles["Normal"],
        fontSize=9,
        textColor=colors.HexColor("#1155cc"),
        spaceAfter=2,
    )
    pitch_style = ParagraphStyle(
        "Pitch",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#5c1a3a"),
        backColor=colors.HexColor("#fdf0f8"),
        spaceAfter=8,
        leftIndent=8,
        rightIndent=8,
        borderPad=6,
    )
    contact_style = ParagraphStyle(
        "Contact",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#1a3a5c"),
        backColor=colors.HexColor("#f0f4fb"),
        spaceAfter=8,
        leftIndent=8,
        rightIndent=8,
        borderPad=6,
    )

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp_path = tmp.name

    doc = SimpleDocTemplate(
        tmp_path,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    story = []

    story.append(Paragraph("🌐 Trade Intelligence Digest", title_style))
    story.append(Paragraph(f"India – Europe | {_date_str()}", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#1a3a5c")))
    story.append(Spacer(1, 0.4 * cm))

    story.append(Paragraph(
        f"Top <b>{len(articles)}</b> trade opportunities curated and scored by AI from "
        "NewsAPI, RSS feeds (India + EU/German sources), and Google News. "
        "Articles are ranked by composite score (Relevance × Credibility × Opportunity) "
        "and grouped by trade direction.",
        body,
    ))
    story.append(Spacer(1, 0.3 * cm))

    if executive_summary:
        exec_header = ParagraphStyle(
            "ExecHeader",
            parent=styles["Normal"],
            fontSize=11,
            textColor=colors.HexColor("#1a3a5c"),
            fontName="Helvetica-Bold",
            spaceAfter=4,
        )
        exec_body = ParagraphStyle(
            "ExecBody",
            parent=styles["Normal"],
            fontSize=10,
            leading=15,
            textColor=colors.HexColor("#1a3a5c"),
            backColor=colors.HexColor("#eef4fb"),
            leftIndent=10,
            rightIndent=10,
            spaceBefore=4,
            spaceAfter=12,
            borderPad=8,
        )
        story.append(Paragraph("📋 Executive Briefing", exec_header))
        for line in executive_summary.split("\n"):
            line = line.strip()
            if line:
                story.append(Paragraph(_esc(line), exec_body))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cccccc")))
        story.append(Spacer(1, 0.2 * cm))

    india_eu, eu_india = _split_by_direction(articles)

    def _render_articles(article_list: list[dict], start_rank: int) -> None:
        for rank, article in enumerate(article_list, start=start_rank):
            for _f in ("title", "source", "published_at", "description", "trade_direction",
                       "summary", "opportunity_note", "monetisation", "action_plan",
                       "contact_targets", "pitch_angle"):
                if isinstance(article.get(_f), list):
                    article[_f] = "\n".join(str(x) for x in article[_f])
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cccccc")))
            story.append(Spacer(1, 0.2 * cm))

            story.append(Paragraph(
                f"#{rank} — {_esc(article.get('title', 'No title'))}",
                section_header,
            ))

            direction_badge = _esc(article.get("trade_direction", "")).replace("→", "->")
            story.append(Paragraph(
                f"Source: <b>{_esc(article.get('source', 'Unknown'))}</b> &nbsp;|&nbsp; "
                f"Published: {_esc(article.get('published_at', 'N/A')[:10])}"
                + (f" &nbsp;|&nbsp; Direction: <b>{direction_badge}</b>" if direction_badge else ""),
                label,
            ))

            url = article.get("url", "")
            if url:
                story.append(Paragraph(f'<link href="{_esc(url)}">{_esc(url)}</link>', link_style))

            score_data = [
                ["Relevance", "Credibility", "Opportunity", "Composite"],
                [
                    _score_bar(article.get("relevance_score", 0)),
                    _score_bar(article.get("credibility_score", 0)),
                    _score_bar(article.get("opportunity_score", 0)),
                    str(article.get("composite_score", 0)),
                ],
            ]
            score_table = Table(score_data, colWidths=[4 * cm, 4 * cm, 4 * cm, 3 * cm])
            score_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a3a5c")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#cccccc")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f7f9fc"), colors.white]),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]))
            story.append(Spacer(1, 0.2 * cm))
            story.append(score_table)
            story.append(Spacer(1, 0.25 * cm))

            summary = article.get("summary", article.get("description", ""))
            if isinstance(summary, list):
                summary = "\n".join(str(x) for x in summary)
            if summary:
                story.append(Paragraph("<b>Summary:</b>", label))
                story.append(Paragraph(_esc(summary), body))

            opp_note = article.get("opportunity_note", "")
            if isinstance(opp_note, list):
                opp_note = "\n".join(str(x) for x in opp_note)
            if opp_note:
                story.append(Paragraph("<b>Why this matters:</b>", label))
                story.append(Paragraph(_esc(opp_note), body))

            monetise = article.get("monetisation", "")
            if isinstance(monetise, list):
                monetise = "\n".join(str(x) for x in monetise)
            if monetise:
                story.append(Paragraph("<b>💰 How to Monetise:</b>", label))
                story.append(Paragraph(_esc(monetise), monetise_style))

            action_plan = article.get("action_plan", "")
            if isinstance(action_plan, list):
                action_plan = "\n".join(str(x) for x in action_plan)
            if action_plan:
                action_style = ParagraphStyle(
                    "ActionPlan",
                    parent=styles["Normal"],
                    fontSize=10,
                    leading=14,
                    textColor=colors.HexColor("#1a3a5c"),
                    backColor=colors.HexColor("#fff8e1"),
                    spaceAfter=8,
                    leftIndent=8,
                    rightIndent=8,
                    borderPad=6,
                )
                story.append(Paragraph("<b>🎯 Action Plan:</b>", label))
                story.append(Paragraph(_esc(action_plan), action_style))

            contact_targets = article.get("contact_targets", "")
            if isinstance(contact_targets, list):
                contact_targets = "\n".join(str(x) for x in contact_targets)
            if contact_targets:
                story.append(Paragraph("<b>🏢 Who to Contact First:</b>", label))
                story.append(Paragraph(_esc(contact_targets), contact_style))

            pitch_angle = article.get("pitch_angle", "")
            if isinstance(pitch_angle, list):
                pitch_angle = "\n".join(str(x) for x in pitch_angle)
            if pitch_angle:
                story.append(Paragraph("<b>✉️ Cold Outreach Opener:</b>", label))
                story.append(Paragraph(_esc(pitch_angle), pitch_style))

            story.append(Spacer(1, 0.3 * cm))

    # Section 1: India Trade News → Europe
    story.append(Paragraph("🇮🇳 India Trade News -> Europe", section_banner))
    story.append(Paragraph(
        "Opportunities where India exports to EU / Germany imports from India.",
        body,
    ))
    if india_eu:
        _render_articles(india_eu, start_rank=1)
    else:
        story.append(Paragraph("No India→EU articles in today's digest.", body))

    # Section 2: EU Trade News → India & Asia
    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph("🇪🇺 EU Trade News -> India &amp; Asia", section_banner))
    story.append(Paragraph(
        "Opportunities where Germany/EU exports to India or enters Asian markets.",
        body,
    ))
    if eu_india:
        _render_articles(eu_india, start_rank=len(india_eu) + 1)
    else:
        story.append(Paragraph("No EU→India articles in today's digest.", body))

    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1a3a5c")))
    story.append(Spacer(1, 0.3 * cm))
    footer_style = ParagraphStyle("Footer", parent=styles["Normal"], fontSize=9,
                                  textColor=colors.HexColor("#444444"), alignment=TA_LEFT, leading=14)
    footer_muted = ParagraphStyle("FooterMuted", parent=styles["Normal"], fontSize=8,
                                  textColor=colors.HexColor("#aaaaaa"), alignment=TA_LEFT)
    story.append(Paragraph("With Best Regards,", footer_style))
    story.append(Paragraph("<b>Saidurga Gowtham Duggirala</b>", footer_style))
    story.append(Paragraph("Managing Director", footer_style))
    story.append(Paragraph("Raaya Global UG", footer_style))
    story.append(Paragraph('<link href="https://www.raayaglobal.de">www.raayaglobal.de</link>', footer_style))
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph("Generated automatically by Trade Intelligence | Powered by Groq AI", footer_muted))

    doc.build(story)

    with open(tmp_path, "rb") as f:
        pdf_bytes = f.read()

    os.unlink(tmp_path)
    return pdf_bytes


# ── HTML email body ───────────────────────────────────────────────────────────

def _render_article_rows(article_list: list[dict], start_rank: int) -> str:
    rows = ""
    for rank, a in enumerate(article_list, start=start_rank):
        url = a.get("url", "#")
        _ap = a.get("action_plan", "")
        if isinstance(_ap, list):
            a = {**a, "action_plan": "\n".join(str(x) for x in _ap)}
        _ct = a.get("contact_targets", "")
        if isinstance(_ct, list):
            a = {**a, "contact_targets": "\n".join(str(x) for x in _ct)}
        _pa = a.get("pitch_angle", "")
        if isinstance(_pa, list):
            a = {**a, "pitch_angle": "\n".join(str(x) for x in _pa)}
        monetise_html = (
            f'<div style="background:#f0faf3;border-left:3px solid #27ae60;'
            f'padding:8px 12px;margin-top:8px;color:#1a5c2a;font-size:13px;">'
            f'<b>💰 How to Monetise:</b><br>{a.get("monetisation","")}</div>'
            if a.get("monetisation") else ""
        )
        action_html = (
            f'<div style="background:#fff8e1;border-left:3px solid #f39c12;'
            f'padding:8px 12px;margin-top:8px;color:#1a3a5c;font-size:13px;">'
            f'<b>🎯 Action Plan:</b><br>{a.get("action_plan","")}</div>'
            if a.get("action_plan") else ""
        )
        contact_html = (
            f'<div style="background:#f0f4fb;border-left:3px solid #1a3a5c;'
            f'padding:8px 12px;margin-top:8px;color:#1a3a5c;font-size:13px;">'
            f'<b>🏢 Who to Contact First:</b><br>{a.get("contact_targets","")}</div>'
            if a.get("contact_targets") else ""
        )
        pitch_html = (
            f'<div style="background:#fdf0f8;border-left:3px solid #c0397a;'
            f'padding:8px 12px;margin-top:8px;color:#5c1a3a;font-size:13px;">'
            f'<b>✉️ Cold Outreach Opener:</b><br><em>{a.get("pitch_angle","")}</em></div>'
            if a.get("pitch_angle") else ""
        )
        rows += f"""
        <tr>
          <td style="padding:16px;border-bottom:1px solid #eee;vertical-align:top;">
            <div style="font-size:11px;color:#888;">#{rank} &nbsp;|&nbsp; {a.get('source','')} &nbsp;|&nbsp; {a.get('published_at','')[:10]}</div>
            <div style="font-size:16px;font-weight:bold;margin:4px 0;">
              <a href="{url}" style="color:#1a3a5c;text-decoration:none;">{a.get('title','')}</a>
            </div>
            <div style="font-size:12px;color:#555;margin-bottom:6px;">{a.get('summary',a.get('description',''))}</div>
            <table style="font-size:11px;border-collapse:collapse;">
              <tr>
                <td style="padding:3px 8px;background:#1a3a5c;color:#fff;border-radius:3px 0 0 3px;">Relevance {a.get('relevance_score',0)}/10</td>
                <td style="padding:3px 8px;background:#2c5f8a;color:#fff;">Credibility {a.get('credibility_score',0)}/10</td>
                <td style="padding:3px 8px;background:#e67e22;color:#fff;border-radius:0 3px 3px 0;">Opportunity {a.get('opportunity_score',0)}/10</td>
              </tr>
            </table>
            {monetise_html}
            {action_html}
            {contact_html}
            {pitch_html}
            <div style="margin-top:8px;font-size:11px;">
              <a href="{url}" style="color:#1155cc;">Read full article →</a>
            </div>
          </td>
        </tr>"""
    return rows


def _build_html(articles: list[dict], executive_summary: str = "") -> str:
    india_eu, eu_india = _split_by_direction(articles)

    section1_rows = _render_article_rows(india_eu, start_rank=1)
    section2_rows = _render_article_rows(eu_india, start_rank=len(india_eu) + 1)

    section1_html = f"""
        <tr><td style="padding:12px 32px;background:#1a3a5c;">
          <div style="color:#fff;font-size:17px;font-weight:bold;">🇮🇳 India Trade News → Europe</div>
          <div style="color:#a8c4e0;font-size:12px;margin-top:2px;">India exports to EU / Germany imports from India</div>
        </td></tr>
        <tr><td>
          <table width="100%" cellpadding="0" cellspacing="0">{section1_rows if section1_rows else '<tr><td style="padding:16px;color:#888;">No India→EU articles today.</td></tr>'}</table>
        </td></tr>"""

    section2_html = f"""
        <tr><td style="padding:12px 32px;background:#2c5f8a;">
          <div style="color:#fff;font-size:17px;font-weight:bold;">🇪🇺 EU Trade News → India &amp; Asia</div>
          <div style="color:#a8c4e0;font-size:12px;margin-top:2px;">Germany/EU exports to India or enters Asian markets</div>
        </td></tr>
        <tr><td>
          <table width="100%" cellpadding="0" cellspacing="0">{section2_rows if section2_rows else '<tr><td style="padding:16px;color:#888;">No EU→India articles today.</td></tr>'}</table>
        </td></tr>"""

    return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;background:#f4f6f8;font-family:Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0">
    <tr><td align="center" style="padding:30px 10px;">
      <table width="660" cellpadding="0" cellspacing="0" style="background:#fff;border-radius:8px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.08);">
        <tr><td style="background:#1a3a5c;padding:28px 32px;">
          <div style="color:#fff;font-size:24px;font-weight:bold;">🌐 Trade Intelligence Digest</div>
          <div style="color:#a8c4e0;font-size:14px;margin-top:4px;">India – Europe &nbsp;|&nbsp; {_date_str()}</div>
        </td></tr>
        <tr><td style="padding:16px 32px;background:#f0f4f8;font-size:13px;color:#555;">
          Top <b>{len(articles)}</b> opportunities ranked by AI composite score, grouped by trade direction. Full report attached as PDF.
        </td></tr>
        {f'''<tr><td style="padding:16px 32px;background:#eef4fb;border-left:4px solid #1a3a5c;">
          <div style="font-size:13px;font-weight:bold;color:#1a3a5c;margin-bottom:8px;">📋 Executive Briefing</div>
          <div style="font-size:13px;color:#333;line-height:1.7;white-space:pre-line;">{executive_summary}</div>
        </td></tr>''' if executive_summary else ''}
        {section1_html}
        {section2_html}
        <tr><td style="padding:24px 32px;background:#f0f4f8;border-top:1px solid #dde3ea;">
          <div style="font-size:13px;color:#333;line-height:1.8;">
            With Best Regards,<br>
            <strong>Saidurga Gowtham Duggirala</strong><br>
            Managing Director<br>
            Raaya Global UG<br>
            <a href="https://www.raayaglobal.de" style="color:#1a3a5c;">www.raayaglobal.de</a>
          </div>
          <div style="margin-top:12px;font-size:10px;color:#aaa;">
            Generated automatically · Powered by Groq AI · See attached PDF for full report with clickable links
          </div>
        </td></tr>
      </table>
    </td></tr>
  </table>
</body>
</html>"""


# ── Sender ────────────────────────────────────────────────────────────────────

def send_digest(articles: list[dict], executive_summary: str = "") -> None:
    gmail_user = os.environ["GMAIL_USER"]
    gmail_password = os.environ["GMAIL_APP_PASSWORD"]
    recipient = os.environ["RECIPIENT_EMAIL"]
    cc_raw = os.environ.get("RECIPIENT_CC", "")
    cc_list = [e.strip() for e in cc_raw.split(",") if e.strip()]

    subject = f"Trade Intelligence Digest — {_date_str()}"

    msg = MIMEMultipart("mixed")
    msg["Subject"] = subject
    msg["From"] = gmail_user
    msg["To"] = recipient
    if cc_list:
        msg["Cc"] = ", ".join(cc_list)

    html_body = _build_html(articles, executive_summary)
    msg.attach(MIMEText(html_body, "html"))

    print("[Email] Building PDF...")
    pdf_bytes = build_pdf(articles, executive_summary)
    pdf_filename = f"trade_intel_{datetime.utcnow().strftime('%Y%m%d')}.pdf"

    attachment = MIMEBase("application", "octet-stream")
    attachment.set_payload(pdf_bytes)
    encoders.encode_base64(attachment)
    attachment.add_header("Content-Disposition", f'attachment; filename="{pdf_filename}"')
    msg.attach(attachment)

    all_recipients = [recipient] + cc_list
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(gmail_user, gmail_password)
        smtp.sendmail(gmail_user, all_recipients, msg.as_string())

    print(f"[Email] Digest sent to {', '.join(all_recipients)} with PDF attachment '{pdf_filename}'.")
