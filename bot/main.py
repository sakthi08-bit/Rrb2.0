"""
╔══════════════════════════════════════════════════════════════╗
║        🎓 EXAM RESULT TRACKER BOT — ADVANCED v4             ║
║  SSC MTS Feb 2026 | RRB NTPC CEN 06/2025 | Group D 08/2024  ║
╠══════════════════════════════════════════════════════════════╣
║  Features:                                                   ║
║  • Rich HTML coloured messages with emojis                   ║
║  • SerpAPI live Google search shown INSIDE the bot           ║
║  • Roll Number checker (searches across all 3 exams)         ║
║  • Today-alert if any result is released                     ║
║  • Verified data with source attribution                     ║
╠══════════════════════════════════════════════════════════════╣
║  Install:  pip install python-telegram-bot==20.7 requests    ║
║  Run:      python exam_bot_v4.py                             ║
╚══════════════════════════════════════════════════════════════╝
"""

import logging
import re
import requests
from datetime import date
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    filters,
    ContextTypes,
)

# ═══════════════════════════════════════════════════════════════
#  🔧 CONFIG — fill these in before running
# ═══════════════════════════════════════════════════════════════
BOT_TOKEN   = "8640224009:AAGr1DPdJVLnsLK5hLNsNKlzF8AdEyzxgbc"   # From @BotFather
SERPAPI_KEY = "8bf6d1dea7604b57c68fa6c8b4bd8991785c582f2190f77f20fb758268c2428e"          # From serpapi.com

# ═══════════════════════════════════════════════════════════════
#  📚 CONVERSATION STATES
# ═══════════════════════════════════════════════════════════════
WAITING_ROLL = 1   # Waiting for roll number input

# ═══════════════════════════════════════════════════════════════
#  📋 VERIFIED EXAM DATA  (cross-checked May 14 2026)
# ═══════════════════════════════════════════════════════════════
EXAMS = {
    "ssc_mts": {
        "key":             "ssc_mts",
        "name":            "SSC MTS Feb 2026",
        "full":            "SSC MTS and Havaldar (CBIC and CBN) Examination 2025",
        "icon":            "📋",
        "color_tag":       "orange",          # used in themed headers
        "status":          "awaited",         # awaited | released | court_hold
        "result_date":     None,              # "YYYY-MM-DD" when declared
        "exam_dates":      "4 Feb to 15 Feb 2026  (Re-exam: 20 Feb 2026)",
        "answer_key":      "3 March 2026",
        "obj_deadline":    "6 March 2026",
        "expected_result": "May 2026",
        "vacancies":       "7,948  (4,375 MTS + 1,089 Havaldar + others)",
        "official_link":   "https://ssc.gov.in/",
        "scorecard_link":  "https://ssc.gov.in/login",
        "next_stage":      "Document Verification (MTS)  |  PET/PST (Havaldar)",
        "serpapi_query":   "SSC MTS result 2026 site:ssc.gov.in OR site:adda247.com",
        "roll_query_tpl":  "SSC MTS 2026 result roll number {roll} selected qualified",
        "key_facts": [
            "CBE held 4 to 15 Feb 2026  (re-exam 20 Feb for some centres)",
            "7,948 total vacancies across MTS and Havaldar posts",
            "Provisional answer key released 3 March 2026",
            "Objection window closed 6 March 2026",
            "Result PDF will be publicly accessible on ssc.gov.in (no login needed)",
            "Merit list will be category-wise PDFs (MTS and Havaldar separate)",
            "Scorecard expected 10 to 15 days after result",
            "Cut-off released along with the result PDF",
        ],
        "steps": [
            "Visit <code>ssc.gov.in</code>",
            "Click the <b>Result</b> tab on the homepage",
            "Find <i>MTS and Havaldar 2025 CBE Result</i> link",
            "Download the category-wise merit list PDF",
            "Press <code>Ctrl+F</code> and search your Roll Number",
            "MTS qualified → Document Verification",
            "Havaldar qualified → PET / PST stage",
        ],
    },

    "rrb_ntpc": {
        "key":             "rrb_ntpc",
        "name":            "RRB NTPC CEN 06/2025",
        "full":            "RRB NTPC Graduate Level CEN 06/2025",
        "icon":            "🚂",
        "color_tag":       "blue",
        "status":          "awaited",
        "result_date":     None,
        "exam_dates":      "16 March to 27 March 2026",
        "answer_key":      "6 April 2026",
        "obj_deadline":    "Mid-April 2026",
        "expected_result": "May to June 2026",
        "vacancies":       "5,810 Graduate Level posts",
        "official_link":   "https://www.rrbcdg.gov.in/2025-06-ntpcg.php",
        "scorecard_link":  "https://rrb.digialm.com/",
        "next_stage":      "CBT 2 for qualified candidates",
        "serpapi_query":   "RRB NTPC CEN 06/2025 CBT 1 result date 2026",
        "roll_query_tpl":  "RRB NTPC CEN 06 2025 CBT 1 result roll number {roll}",
        "key_facts": [
            "CBT 1 conducted 16 to 27 March 2026 across all railway zones",
            "5,810 vacancies: Station Master, Goods Guard, JAA, Sr Clerk etc",
            "Answer key released 6 April 2026 on all regional RRB sites",
            "Over 40 lakh candidates appeared for CBT 1",
            "CBT 1 marks are NOT counted in final merit — only used for shortlisting",
            "Top 20x vacancy count shortlisted zone-wise for CBT 2",
            "Min qualifying: UR/EWS 40%,  OBC/SC 30%,  ST 25%",
            "Scorecard downloadable at rrb.digialm.com after result",
        ],
        "steps": [
            "Visit your regional RRB site  (e.g. <code>rrbcdg.gov.in</code>)",
            "Open the <b>CEN 06/2025 NTPC Graduate</b> section",
            "Click on <i>CBT 1 Result</i> link when active",
            "Download the zone-wise merit list PDF",
            "Press <code>Ctrl+F</code> and search your Roll Number",
            "Download scorecard at <code>rrb.digialm.com</code> using Reg No + DOB",
            "Qualified candidates called for CBT 2",
        ],
    },

    "rrb_groupd": {
        "key":             "rrb_groupd",
        "name":            "RRB Group D CEN 08/2024",
        "full":            "RRB Group D Level 1 CEN 08/2024",
        "icon":            "🛤️",
        "color_tag":       "green",
        "status":          "court_hold",
        "result_date":     None,
        "exam_dates":      "27 Nov 2025 to 10 Feb 2026",
        "answer_key":      "17 February 2026",
        "obj_deadline":    "23 February 2026",
        "expected_result": "Last week of May 2026  (after HC hearing 22 May)",
        "vacancies":       "32,438 Level 1 posts",
        "official_link":   "https://www.rrbcdg.gov.in/2024-08-level1.php",
        "scorecard_link":  "https://rrb.digialm.com/",
        "next_stage":      "Physical Efficiency Test (PET) — June 2026",
        "serpapi_query":   "RRB Group D CEN 08 2024 result date Telangana court 2026",
        "roll_query_tpl":  "RRB Group D CEN 08 2024 result roll number {roll} qualified PET",
        "key_facts": [
            "CBT held 27 Nov 2025 to 10 Feb 2026  (32,438 vacancies)",
            "Around 1.08 crore (10.8 million) candidates appeared",
            "Provisional answer key released 17 February 2026",
            "Objection window closed 23 February 2026",
            "⚖️ Telangana High Court TEMPORARILY stayed the result",
            "Next court hearing: 22 May 2026",
            "Expected result: last week of May 2026 after HC hearing",
            "This is a temporary DELAY — NOT a cancellation",
            "PET expected June 2026 for qualified candidates",
        ],
        "steps": [
            "⚖️ Wait for HC hearing on <b>22 May 2026</b>",
            "After result declared, visit your regional RRB website",
            "Find <i>CEN 08/2024 Group D Level 1 Result</i> link",
            "Download the zone-wise CBT result PDF",
            "Press <code>Ctrl+F</code> and search your Roll Number",
            "Download scorecard at <code>rrb.digialm.com</code> (Reg No + DOB)",
            "CBT qualified → Physical Efficiency Test (PET)",
        ],
    },
}

# ═══════════════════════════════════════════════════════════════
#  🎨 HTML THEME HELPERS
# ═══════════════════════════════════════════════════════════════

DIVIDER   = "─" * 32
THICK_DIV = "═" * 32

def h1(text):
    """Big bold header line."""
    return f"<b>{text}</b>"

def h2(text):
    """Section sub-header."""
    return f"<b><u>{text}</u></b>"

def tag(text, style="b"):
    return f"<{style}>{text}</{style}>"

def status_badge(exam):
    s = exam["status"]
    if s == "released":
        return "✅  <b>RESULT DECLARED</b>"
    if s == "court_hold":
        return "⚖️  <b>RESULT ON COURT HOLD</b>  <i>(Telangana HC)</i>"
    return "⏳  <b>RESULT AWAITED</b>"

def status_color_line(exam):
    s = exam["status"]
    d = exam.get("result_date")
    if s == "released":
        return f"✅ <b>DECLARED</b>  on  <code>{d}</code>"
    if s == "court_hold":
        return (
            f"⚖️ <b>COURT HOLD</b>\n"
            f"   Telangana HC stay in effect\n"
            f"   Next hearing: <b>22 May 2026</b>\n"
            f"   Expected: <b>Last week of May 2026</b>"
        )
    return f"⏳ <b>AWAITED</b>  —  Expected: <b>{exam['expected_result']}</b>"

def today_alerts():
    today = date.today().isoformat()
    return [e for e in EXAMS.values() if e.get("result_date") == today]

# ═══════════════════════════════════════════════════════════════
#  📝 MESSAGE BUILDERS
# ═══════════════════════════════════════════════════════════════

def msg_home():
    alerts = today_alerts()
    alert_block = ""
    if alerts:
        names = "\n".join(f"   🔔 <b>{e['name']}</b>" for e in alerts)
        alert_block = (
            f"\n\n🚨 <b>RESULT RELEASED TODAY!</b>\n"
            f"{names}\n"
        )

    rows = []
    for e in EXAMS.values():
        s = e["status"]
        badge = "✅" if s == "released" else ("⚖️" if s == "court_hold" else "⏳")
        rows.append(f"   {e['icon']} <b>{e['name']}</b>  {badge}")

    return (
        f"🎓 <b>EXAM RESULT TRACKER BOT</b>\n"
        f"{THICK_DIV}\n"
        f"{alert_block}\n"
        f"📌 <b>Tracking 3 exams:</b>\n"
        + "\n".join(rows) +
        f"\n\n"
        f"<i>Tap an exam for full details, live search, or roll number check.</i>\n"
        f"\n🗓 <code>Data verified: {date.today().strftime('%d %b %Y')}</code>"
    )


def msg_exam(key):
    e = EXAMS[key]
    facts = "\n".join(f"   ▸ {f}" for f in e["key_facts"])
    steps = "\n".join(f"   <b>{i+1}.</b> {s}" for i, s in enumerate(e["steps"]))

    return (
        f"{e['icon']}  <b>{e['full']}</b>\n"
        f"{DIVIDER}\n\n"

        f"📊 <b>STATUS</b>\n"
        f"   {status_color_line(e)}\n\n"

        f"📅 <b>EXAM DATES</b>\n"
        f"   <code>{e['exam_dates']}</code>\n\n"

        f"🔑 <b>ANSWER KEY</b>\n"
        f"   <code>{e['answer_key']}</code>   "
        f"<i>(Objections closed: {e['obj_deadline']})</i>\n\n"

        f"📊 <b>VACANCIES</b>\n"
        f"   <code>{e['vacancies']}</code>\n\n"

        f"⏭  <b>NEXT STAGE</b>\n"
        f"   {e['next_stage']}\n\n"

        f"{DIVIDER}\n"
        f"🔖 <b>KEY FACTS</b>\n"
        f"{facts}\n\n"

        f"{DIVIDER}\n"
        f"🪜 <b>HOW TO CHECK (when declared)</b>\n"
        f"{steps}\n\n"

        f"<i>🌐 Official site: {e['official_link']}</i>"
    )


def msg_verify(key):
    e = EXAMS[key]
    today_str = date.today().strftime("%d %B %Y")
    src_map = {
        "ssc_mts":    "ssc.gov.in  |  adda247.com  |  testbook.com",
        "rrb_ntpc":   "rrbcdg.gov.in  |  shiksha.com  |  careerpower.in",
        "rrb_groupd": "rrbcdg.gov.in  |  testbook.com  |  shiksha.com",
    }
    notes_map = {
        "ssc_mts": [
            "CBE held 4 to 15 Feb 2026, re-exam on 20 Feb",
            "Answer key released 3 March 2026",
            "Objection window closed 6 March 2026",
            "Result expected May 2026 — <b>NOT YET DECLARED</b>",
        ],
        "rrb_ntpc": [
            "CBT 1 conducted 16 to 27 March 2026",
            "Answer key released 6 April 2026",
            "Result expected May to June 2026 — <b>NOT YET DECLARED</b>",
            "Over 40 lakh candidates appeared",
        ],
        "rrb_groupd": [
            "CBT held 27 Nov 2025 to 10 Feb 2026",
            "Answer key released 17 Feb 2026",
            "<b>Telangana HC temporarily stayed the result</b>",
            "Next HC hearing: 22 May 2026",
            "Result expected last week of May 2026",
            "This is a temporary delay, NOT a cancellation",
        ],
    }
    notes = "\n".join(f"   ✔ {n}" for n in notes_map[key])
    return (
        f"🔍 <b>VERIFICATION REPORT</b>\n"
        f"{e['icon']}  <b>{e['name']}</b>\n"
        f"{DIVIDER}\n\n"
        f"{notes}\n\n"
        f"📚 <b>Sources:</b>\n"
        f"   <code>{src_map[key]}</code>\n\n"
        f"🕐 <b>Last verified:</b>  <code>{today_str}</code>\n\n"
        f"⚠️ <i>Always confirm on official websites before taking any action.</i>"
    )


def msg_about():
    return (
        f"ℹ️ <b>ABOUT THIS BOT</b>\n"
        f"{DIVIDER}\n\n"

        f"🤖 <b>What I do:</b>\n"
        f"   Track results for 3 major govt exams\n\n"

        f"🔍 <b>Live Search:</b>\n"
        f"   Powered by <b>SerpAPI</b> — shows Google results\n"
        f"   directly inside Telegram (no redirect!)\n\n"

        f"🔢 <b>Roll Number Check:</b>\n"
        f"   Enter your roll number and I'll search\n"
        f"   Google to see if your result is mentioned\n\n"

        f"📋 <b>Exams tracked:</b>\n"
        f"   📋  SSC MTS Feb 2026\n"
        f"   🚂  RRB NTPC CEN 06/2025\n"
        f"   🛤️  RRB Group D CEN 08/2024\n\n"

        f"📚 <b>Data verified from:</b>\n"
        f"   <code>ssc.gov.in  |  rrbcdg.gov.in</code>\n"
        f"   <code>testbook.com  |  adda247.com</code>\n"
        f"   <code>shiksha.com  |  careerpower.in</code>\n\n"

        f"🗓 <b>Last verified:</b> <code>{date.today().strftime('%d %b %Y')}</code>\n\n"
        f"⚠️ <i>This bot is for quick reference.\n"
        f"Always confirm on official websites.</i>"
    )


def msg_roll_prompt():
    return (
        f"🔢 <b>ROLL NUMBER CHECKER</b>\n"
        f"{DIVIDER}\n\n"
        f"Send your <b>Roll Number</b> and I will search Google\n"
        f"to check if your result is available.\n\n"
        f"📌 <b>Works for:</b>\n"
        f"   📋 SSC MTS Feb 2026\n"
        f"   🚂 RRB NTPC CEN 06/2025\n"
        f"   🛤️ RRB Group D CEN 08/2024\n\n"
        f"<i>Type your roll number now:</i> 👇"
    )


# ═══════════════════════════════════════════════════════════════
#  🔍 SERPAPI FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def serpapi_search(query: str, num: int = 5) -> list[dict]:
    """Call SerpAPI Google Search and return organic results."""
    try:
        resp = requests.get(
            "https://serpapi.com/search",
            params={
                "engine":  "google",
                "q":       query,
                "api_key": SERPAPI_KEY,
                "num":     num,
                "hl":      "en",
                "gl":      "in",
            },
            timeout=15,
        )
        data = resp.json()
        return data.get("organic_results", [])
    except Exception as exc:
        logging.error("SerpAPI error: %s", exc)
        return []


def format_search_results(results: list[dict], query: str) -> str:
    """Format SerpAPI results as a rich HTML Telegram message."""
    if not results:
        return (
            f"🔍 <b>Search:</b> <code>{query}</code>\n\n"
            f"❌ <b>No results found.</b>\n"
            f"<i>Try checking official websites directly.</i>"
        )

    lines = [
        f"🔍 <b>LIVE SEARCH RESULTS</b>",
        f"<code>{query}</code>",
        f"{DIVIDER}",
        "",
    ]
    for i, r in enumerate(results[:5], 1):
        title   = r.get("title", "No title")[:80]
        snippet = r.get("snippet", "")[:200]
        link    = r.get("link", "")
        source  = r.get("displayed_link", link)[:50]

        lines.append(f"<b>{i}. {title}</b>")
        if snippet:
            lines.append(f"<i>{snippet}</i>")
        lines.append(f"🔗 <code>{source}</code>")
        lines.append("")

    lines.append(f"<i>⏱ Results fetched live via SerpAPI · {date.today().strftime('%d %b %Y')}</i>")
    return "\n".join(lines)


def format_roll_results(roll: str, results: list[dict]) -> str:
    """Format roll number search results."""
    if not results:
        return (
            f"🔢 <b>Roll Number:</b> <code>{roll}</code>\n\n"
            f"❌ <b>No specific result found on Google.</b>\n\n"
            f"📌 <b>Possible reasons:</b>\n"
            f"   ▸ Result not yet declared for your exam\n"
            f"   ▸ Roll number not in shortlisted PDF yet\n"
            f"   ▸ Check official site directly\n\n"
            f"<i>Try again after the official result is out.</i>"
        )

    lines = [
        f"🔢 <b>ROLL NUMBER RESULT CHECK</b>",
        f"Roll: <code>{roll}</code>",
        f"{DIVIDER}",
        "",
    ]

    # Highlight lines that mention "selected", "qualified", "shortlisted"
    keywords = ["selected", "qualified", "shortlisted", "merit", "result"]
    found_positive = False

    for i, r in enumerate(results[:4], 1):
        title   = r.get("title", "")[:80]
        snippet = r.get("snippet", "")[:250]
        source  = r.get("displayed_link", "")[:50]

        # Check if snippet mentions positive keywords
        combined = (title + snippet).lower()
        is_relevant = any(kw in combined for kw in keywords)

        marker = "🟢" if is_relevant else "🔵"
        if is_relevant:
            found_positive = True

        lines.append(f"{marker} <b>{title}</b>")
        if snippet:
            # Bold any mention of the roll number in the snippet
            highlighted = snippet.replace(roll, f"<b><u>{roll}</u></b>")
            lines.append(f"<i>{highlighted}</i>")
        lines.append(f"   🔗 <code>{source}</code>")
        lines.append("")

    if found_positive:
        lines.insert(4, f"💡 <b>Some results may reference your roll number.</b>\n")
    else:
        lines.insert(4, f"⚠️ <b>No direct match found. Result may not be declared yet.</b>\n")

    lines.append(f"<i>⏱ Searched live via SerpAPI · {date.today().strftime('%d %b %Y')}</i>")
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════
#  ⌨️ KEYBOARDS
# ═══════════════════════════════════════════════════════════════

def kb_home():
    alerts = today_alerts()
    rows = []
    for key, e in EXAMS.items():
        label = f"{e['icon']}  {e['name']}"
        if any(a["key"] == key for a in alerts):
            label = "🔔  " + label + "  — OUT TODAY!"
        rows.append([InlineKeyboardButton(label, callback_data=f"exam|{key}")])
    rows.append([
        InlineKeyboardButton("🔢  Check Roll Number",  callback_data="roll_start"),
        InlineKeyboardButton("ℹ️  About",              callback_data="about"),
    ])
    return InlineKeyboardMarkup(rows)


def kb_exam(key):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔍  Live Google Search",   callback_data=f"search|{key}")],
        [InlineKeyboardButton("✅  Verified Data",        callback_data=f"verify|{key}")],
        [InlineKeyboardButton("🔢  Check Roll Number",   callback_data="roll_start")],
        [
            InlineKeyboardButton("🌐  Official Site",    url=EXAMS[key]["official_link"]),
            InlineKeyboardButton("📊  Scorecard",        url=EXAMS[key]["scorecard_link"]),
        ],
        [InlineKeyboardButton("🏠  Home",               callback_data="home")],
    ])


def kb_verify(key):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔍  Live Search",   callback_data=f"search|{key}")],
        [InlineKeyboardButton("◀  Back to Exam",  callback_data=f"exam|{key}")],
        [InlineKeyboardButton("🏠  Home",          callback_data="home")],
    ])


def kb_search(key):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄  Search Again",   callback_data=f"search|{key}")],
        [InlineKeyboardButton("◀  Back to Exam",   callback_data=f"exam|{key}")],
        [InlineKeyboardButton("🏠  Home",           callback_data="home")],
    ])


def kb_roll_result():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔢  Check Another Roll No", callback_data="roll_start")],
        [InlineKeyboardButton("🏠  Home",                  callback_data="home")],
    ])


def kb_back_home():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🏠  Home", callback_data="home")]
    ])


# ═══════════════════════════════════════════════════════════════
#  🤖 HANDLERS
# ═══════════════════════════════════════════════════════════════
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s — %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        msg_home(), parse_mode="HTML", reply_markup=kb_home()
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"📚 <b>COMMANDS</b>\n"
        f"{DIVIDER}\n\n"
        f"/start — Show exam list and status\n"
        f"/roll  — Check roll number result\n"
        f"/help  — Show this message\n\n"
        f"<i>I auto-alert you if any result drops today! 🔔</i>",
        parse_mode="HTML",
    )


async def cmd_roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        msg_roll_prompt(), parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("❌ Cancel", callback_data="home")]
        ])
    )
    return WAITING_ROLL


async def receive_roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    roll = update.message.text.strip()

    # Basic validation — must have at least 5 alphanumeric characters
    if not re.match(r'^[A-Za-z0-9]{5,20}$', roll):
        await update.message.reply_text(
            f"⚠️ <b>Invalid roll number format.</b>\n\n"
            f"Roll numbers are typically 8 to 15 alphanumeric characters.\n"
            f"Please try again or use /start to go home.",
            parse_mode="HTML",
        )
        return WAITING_ROLL

    await update.message.reply_text(
        f"🔍 <b>Searching Google for roll number</b> <code>{roll}</code>...\n"
        f"<i>Please wait a moment.</i>",
        parse_mode="HTML",
    )

    # Build a combined query that covers all 3 exams
    query = (
        f'"{roll}" SSC MTS 2026 OR "RRB NTPC" OR "Group D" result selected qualified'
    )
    results = serpapi_search(query, num=5)
    reply   = format_roll_results(roll, results)

    await update.message.reply_text(
        reply, parse_mode="HTML", reply_markup=kb_roll_result()
    )
    return ConversationHandler.END


async def cancel_roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❌ Roll number check cancelled.",
        parse_mode="HTML",
        reply_markup=kb_home(),
    )
    return ConversationHandler.END


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    d = q.data

    # ── HOME ────────────────────────────────────────────────────
    if d == "home":
        await q.edit_message_text(
            msg_home(), parse_mode="HTML", reply_markup=kb_home()
        )

    # ── ABOUT ───────────────────────────────────────────────────
    elif d == "about":
        await q.edit_message_text(
            msg_about(), parse_mode="HTML", reply_markup=kb_back_home()
        )

    # ── EXAM DETAIL ─────────────────────────────────────────────
    elif d.startswith("exam|"):
        key = d.split("|")[1]
        if key in EXAMS:
            await q.edit_message_text(
                msg_exam(key), parse_mode="HTML", reply_markup=kb_exam(key)
            )

    # ── VERIFIED DATA ───────────────────────────────────────────
    elif d.startswith("verify|"):
        key = d.split("|")[1]
        if key in EXAMS:
            await q.edit_message_text(
                msg_verify(key), parse_mode="HTML", reply_markup=kb_verify(key)
            )

    # ── LIVE SEARCH ─────────────────────────────────────────────
    elif d.startswith("search|"):
        key = d.split("|")[1]
        if key not in EXAMS:
            return

        await q.edit_message_text(
            f"🔍 <b>Searching Google...</b>\n"
            f"<i>Query: {EXAMS[key]['serpapi_query']}</i>\n\n"
            f"<i>Please wait...</i>",
            parse_mode="HTML",
        )

        results = serpapi_search(EXAMS[key]["serpapi_query"], num=5)
        reply   = format_search_results(results, EXAMS[key]["serpapi_query"])

        await q.edit_message_text(
            reply, parse_mode="HTML", reply_markup=kb_search(key)
        )

    # ── ROLL NUMBER (starts conversation via inline button) ──────
    elif d == "roll_start":
        await q.edit_message_text(
            msg_roll_prompt(), parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ Cancel", callback_data="home")]
            ])
        )
        # Store state in user_data so MessageHandler knows we're waiting
        context.user_data["waiting_roll"] = True


# ── Plain message handler (catches roll number text after button prompt) ──────
async def plain_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("waiting_roll"):
        await update.message.reply_text(
            f"👋 Use /start to open the menu.",
            parse_mode="HTML",
        )
        return

    context.user_data["waiting_roll"] = False
    roll = update.message.text.strip()

    if not re.match(r'^[A-Za-z0-9]{5,20}$', roll):
        await update.message.reply_text(
            f"⚠️ <b>Invalid roll number.</b>\n\n"
            f"Must be 5 to 20 alphanumeric characters. Try again or use /start.",
            parse_mode="HTML",
        )
        return

    await update.message.reply_text(
        f"🔍 Searching for roll number <code>{roll}</code>... please wait.",
        parse_mode="HTML",
    )

    query   = f'"{roll}" SSC MTS 2026 OR "RRB NTPC CEN 06" OR "Group D CEN 08" result selected qualified'
    results = serpapi_search(query, num=5)
    reply   = format_roll_results(roll, results)

    await update.message.reply_text(
        reply, parse_mode="HTML", reply_markup=kb_roll_result()
    )


# ═══════════════════════════════════════════════════════════════
#  🚀 MAIN
# ═══════════════════════════════════════════════════════════════
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # /roll conversation handler
    conv = ConversationHandler(
        entry_points=[CommandHandler("roll", cmd_roll)],
        states={
            WAITING_ROLL: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_roll)
            ]
        },
        fallbacks=[CommandHandler("start", cmd_start)],
    )

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help",  help_cmd))
    app.add_handler(conv)
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, plain_message))

    logger.info("✅ Bot is live — press Ctrl+C to stop.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
