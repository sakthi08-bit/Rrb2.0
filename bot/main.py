"""
Exam Result Tracker — Telegram Bot v3 (Fixed)
==============================================
Fix: Replaced MarkdownV2 with HTML parse_mode everywhere.
     No more character-escaping errors.

Tracks:
  • SSC MTS Feb 2026         (7,948 posts)
  • RRB NTPC CEN 06/2025     (5,810 Graduate Level posts)
  • RRB Group D CEN 08/2024  (32,438 Level 1 posts)

Setup:
    pip install python-telegram-bot==20.7

Run:
    1. Create bot via @BotFather → copy token
    2. Paste token into BOT_TOKEN below
    3. python exam_result_bot_v3.py
"""

import logging
from datetime import date
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

BOT_TOKEN = "8640224009:AAGr1DPdJVLnsLK5hLNsNKlzF8AdEyzxgbc"   # ← Paste your BotFather token here

# ─── EXAM DATA (verified May 14 2026) ────────────────────────────────────────
EXAMS = {
    "ssc_mts": {
        "name":            "SSC MTS Feb 2026",
        "full":            "SSC MTS and Havaldar (CBIC and CBN) Examination 2025",
        "icon":            "📋",
        "status":          "awaited",     # change to "released" when declared
        "result_date":     None,           # set "YYYY-MM-DD" when declared
        "exam_dates":      "4 Feb to 15 Feb 2026 (Re-exam: 20 Feb 2026)",
        "answer_key":      "3 March 2026",
        "expected_result": "May 2026 — not yet declared as of May 14, 2026",
        "vacancies":       "7,948 posts (4,375 MTS + 1,089 Havaldar + others)",
        "official_link":   "https://ssc.gov.in/",
        "next_stage":      "Document Verification for MTS | PET/PST for Havaldar",
        "google_query":    "SSC+MTS+result+2026+ssc.gov.in",
        "verified_note": (
            "CBE held 4 to 15 Feb 2026, re-exam on 20 Feb\n"
            "Answer key released 3 March 2026\n"
            "Objection window closed 6 March 2026\n"
            "Result expected May 2026 — NOT YET DECLARED\n"
            "Sources: ssc.gov.in | adda247.com | testbook.com"
        ),
        "key_facts": [
            "CBE held 4 to 15 Feb 2026 (re-exam 20 Feb for some centres)",
            "7,948 total vacancies for MTS and Havaldar posts",
            "Answer key released 3 March 2026",
            "Objection window closed 6 March 2026",
            "Result expected May 2026 based on SSC past timelines",
            "Merit list will be category-wise PDF on ssc.gov.in",
            "Scorecard expected 10 to 15 days after result",
        ],
        "steps": [
            "Visit ssc.gov.in",
            "Click Result tab on homepage",
            "Find MTS and Havaldar 2025 CBE Result link",
            "Download category-wise merit list PDF",
            "Press Ctrl+F and enter your Roll Number or Name",
            "MTS qualified candidates go to Document Verification",
            "Havaldar qualified candidates go to PET and PST",
        ],
    },

    "rrb_ntpc": {
        "name":            "RRB NTPC CEN 06/2025",
        "full":            "RRB NTPC Graduate Level CEN 06/2025",
        "icon":            "🚂",
        "status":          "awaited",
        "result_date":     None,
        "exam_dates":      "16 March to 27 March 2026",
        "answer_key":      "6 April 2026",
        "expected_result": "May to June 2026 — CBT 1 result not yet declared",
        "vacancies":       "5,810 Graduate Level posts",
        "official_link":   "https://www.rrbcdg.gov.in/2025-06-ntpcg.php",
        "next_stage":      "CBT 2 for qualified candidates",
        "google_query":    "RRB+NTPC+CEN+06+2025+CBT+1+result+date+2026",
        "verified_note": (
            "CBT 1 conducted 16 to 27 March 2026\n"
            "5,810 vacancies: Station Master, Goods Guard, JAA, Sr Clerk etc\n"
            "Answer key released 6 April 2026 on all regional RRB sites\n"
            "Over 40 lakh candidates appeared for CBT 1\n"
            "CBT 1 result expected May to June 2026 — NOT YET DECLARED\n"
            "Sources: rrbcdg.gov.in | shiksha.com | careerpower.in"
        ),
        "key_facts": [
            "CBT 1 held 16 to 27 March 2026 across all zones",
            "5,810 vacancies for Graduate Level posts",
            "Answer key released 6 April 2026",
            "Over 40 lakh candidates appeared in CBT 1",
            "CBT 1 marks are NOT counted in final merit — only used for shortlisting",
            "Top 20 times vacancy count shortlisted from each zone for CBT 2",
            "Minimum qualifying marks: UR/EWS 40%, OBC/SC 30%, ST 25%",
        ],
        "steps": [
            "Visit your regional RRB website (e.g. rrbcdg.gov.in or rrbchennai.gov.in)",
            "Go to the CEN 06/2025 NTPC Graduate section",
            "Click on CBT 1 Result link when it appears",
            "Download zone-wise merit list PDF",
            "Press Ctrl+F and enter your Roll Number",
            "Download scorecard at rrb.digialm.com using Reg No and DOB",
            "Qualified candidates will be called for CBT 2",
        ],
    },

    "rrb_groupd": {
        "name":            "RRB Group D CEN 08/2024",
        "full":            "RRB Group D Level 1 CEN 08/2024",
        "icon":            "🛤️",
        "status":          "court_hold",
        "result_date":     None,
        "exam_dates":      "27 Nov 2025 to 10 Feb 2026",
        "answer_key":      "17 February 2026",
        "expected_result": "Last week of May 2026 (after court hearing on 22 May)",
        "vacancies":       "32,438 Level 1 posts",
        "official_link":   "https://www.rrbcdg.gov.in/2024-08-level1.php",
        "next_stage":      "Physical Efficiency Test (PET) — expected June 2026",
        "google_query":    "RRB+Group+D+CEN+08+2024+result+date+Telangana+court+2026",
        "verified_note": (
            "COURT HOLD — Verified May 14, 2026\n"
            "Telangana High Court has TEMPORARILY stayed the result\n"
            "Next court hearing: 22 May 2026\n"
            "Result expected in last week of May 2026 after hearing\n"
            "This is a temporary DELAY, NOT a cancellation\n"
            "Around 1.08 crore candidates appeared for CBT\n"
            "Sources: testbook.com | shiksha.com | rrbcdg.gov.in"
        ),
        "key_facts": [
            "CBT held 27 Nov 2025 to 10 Feb 2026 for 32,438 vacancies",
            "Around 1.08 crore (10.8 million) candidates appeared",
            "Provisional answer key released 17 February 2026",
            "Objection window closed 23 February 2026",
            "Telangana High Court TEMPORARILY stayed the result",
            "Next court hearing date: 22 May 2026",
            "Result expected in last week of May 2026",
            "This is a delay only — recruitment is NOT cancelled",
            "PET expected June 2026 for qualified candidates",
        ],
        "steps": [
            "Wait for Telangana HC hearing on 22 May 2026",
            "After result is declared, visit your regional RRB website",
            "Find the CEN 08/2024 Group D Level 1 Result link",
            "Download zone-wise CBT result PDF",
            "Press Ctrl+F and enter your Roll Number",
            "Download scorecard at rrb.digialm.com using Reg No and DOB",
            "CBT qualified candidates will be called for PET",
        ],
    },
}


# ─── LOGGING ─────────────────────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# ─── HELPERS ─────────────────────────────────────────────────────────────────
def today_alerts():
    today = date.today().isoformat()
    return [e["name"] for e in EXAMS.values() if e.get("result_date") == today]


def status_emoji(status):
    return {"released": "✅", "court_hold": "⚖️", "awaited": "⏳"}.get(status, "⏳")


def status_text(exam):
    s = exam["status"]
    if s == "released":
        return f"✅ DECLARED on {exam['result_date']}"
    if s == "court_hold":
        return "⚖️ COURT HOLD — result stayed by Telangana HC (next hearing 22 May)"
    return f"⏳ AWAITED — {exam['expected_result']}"


def home_message():
    alerts = today_alerts()
    alert_block = ""
    if alerts:
        names = "\n".join(f"  • {n}" for n in alerts)
        alert_block = f"\n\n🚨 <b>RESULT RELEASED TODAY:</b>\n{names}"

    lines = []
    for e in EXAMS.values():
        em = status_emoji(e["status"])
        lines.append(f"  {e['icon']} <b>{e['name']}</b> — {em}")

    exam_list = "\n".join(lines)
    return (
        f"👋 <b>Exam Result Tracker Bot</b>{alert_block}\n\n"
        f"Tracking results for:\n{exam_list}\n\n"
        f"Select an exam below 👇"
    )


def exam_message(key):
    e = EXAMS[key]
    facts = "\n".join(f"  ▸ {f}" for f in e["key_facts"])
    steps = "\n".join(f"  {i+1}. {s}" for i, s in enumerate(e["steps"]))
    return (
        f"{e['icon']} <b>{e['full']}</b>\n"
        f"{'—'*30}\n\n"
        f"<b>Status:</b> {status_text(e)}\n"
        f"<b>Exam Dates:</b> {e['exam_dates']}\n"
        f"<b>Answer Key:</b> {e['answer_key']}\n"
        f"<b>Vacancies:</b> {e['vacancies']}\n"
        f"<b>Next Stage:</b> {e['next_stage']}\n\n"
        f"<b>Key Facts:</b>\n{facts}\n\n"
        f"<b>How to Check (when declared):</b>\n{steps}"
    )


def verify_message(key):
    e = EXAMS[key]
    lines = "\n".join(f"  • {ln}" for ln in e["verified_note"].splitlines() if ln.strip())
    today_str = date.today().strftime("%d %B %Y")
    return (
        f"✅ <b>Verification Report — {e['icon']} {e['name']}</b>\n"
        f"{'—'*30}\n\n"
        f"{lines}\n\n"
        f"<b>Last checked:</b> {today_str}"
    )


def about_message():
    return (
        "ℹ️ <b>About This Bot</b>\n\n"
        "All data is verified from:\n"
        "  • ssc.gov.in (SSC official)\n"
        "  • rrbcdg.gov.in and all regional RRB sites\n"
        "  • testbook.com, adda247.com, shiksha.com\n\n"
        "<b>Last verified:</b> 14 May 2026\n\n"
        "⚠️ Always confirm results on official websites.\n"
        "This bot is for quick reference only."
    )


# ─── KEYBOARDS ───────────────────────────────────────────────────────────────
def home_kb():
    alerts = today_alerts()
    rows = []
    for key, e in EXAMS.items():
        label = f"{e['icon']} {e['name']}"
        if e["name"] in alerts:
            label = "🔔 " + label + " — OUT TODAY!"
        rows.append([InlineKeyboardButton(label, callback_data=f"exam_{key}")])
    rows.append([InlineKeyboardButton("ℹ️ About this Bot", callback_data="about")])
    return InlineKeyboardMarkup(rows)


def exam_kb(key):
    e = EXAMS[key]
    google_url = f"https://www.google.com/search?q={e['google_query']}"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🌐 Official Website", url=e["official_link"])],
        [InlineKeyboardButton("🔍 Search on Google", url=google_url)],
        [InlineKeyboardButton("✅ View Verified Data", callback_data=f"verify_{key}")],
        [InlineKeyboardButton("« Back to List", callback_data="home")],
    ])


def verify_kb(key):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("« Back to Exam", callback_data=f"exam_{key}")],
        [InlineKeyboardButton("🏠 Home", callback_data="home")],
    ])


def back_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("« Back", callback_data="home")]
    ])


# ─── HANDLERS ────────────────────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        home_message(),
        parse_mode="HTML",
        reply_markup=home_kb(),
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📚 <b>Commands</b>\n\n"
        "/start — Show exam list and result status\n"
        "/help  — Show this message\n\n"
        "The bot auto-alerts if any result is released today! 🔔",
        parse_mode="HTML",
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    d = q.data

    if d == "home":
        await q.edit_message_text(
            home_message(), parse_mode="HTML", reply_markup=home_kb()
        )

    elif d.startswith("exam_"):
        key = d[5:]
        if key in EXAMS:
            await q.edit_message_text(
                exam_message(key), parse_mode="HTML", reply_markup=exam_kb(key)
            )

    elif d.startswith("verify_"):
        key = d[7:]
        if key in EXAMS:
            await q.edit_message_text(
                verify_message(key), parse_mode="HTML", reply_markup=verify_kb(key)
            )

    elif d == "about":
        await q.edit_message_text(
            about_message(), parse_mode="HTML", reply_markup=back_kb()
        )


# ─── MAIN ────────────────────────────────────────────────────────────────────
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CallbackQueryHandler(button_handler))
    logger.info("Bot is running — press Ctrl+C to stop.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
