"""
SSC MTS & RRB Exam Result Telegram Bot
=======================================
Requirements:
    pip install python-telegram-bot==20.7 requests

Setup:
    1. Create a bot via @BotFather on Telegram → get TOKEN
    2. Replace BOT_TOKEN below with your token
    3. Run: python exam_result_bot.py

Features:
    - /start  → Shows 3 exam buttons
    - Select exam → Shows result status, date, and official link
    - Auto-alert if any result was released TODAY
    - Uses live web search via Google for latest updates
"""

import logging
import asyncio
from datetime import date
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# ─── CONFIG ──────────────────────────────────────────────────────────────────
BOT_TOKEN = "8640224009:AAGr1DPdJVLnsLK5hLNsNKlzF8AdEyzxgbc"   # Replace with your BotFather token

# ─── EXAM DATA (update these when new results are announced) ─────────────────
# Format: "YYYY-MM-DD" for released results, None if not yet released
EXAMS = {
    "ssc_mts": {
        "name": "SSC MTS 2026",
        "full_name": "SSC Multi-Tasking Staff (MTS) & Havaldar 2024",
        "icon": "📋",
        "status": "released",
        "result_date": "none",   # Final result declared date
        "result_link": "https://ssc.gov.in/",
        "description": (
            "SSC MTS & Havaldar 2024 Final Result has been declared. "
            "The merit list PDF is available on the official SSC website. "
            "Selected candidates are shortlisted for appointment / PET & PST (Havaldar)."
        ),
        "steps": (
            "1. Visit ssc.gov.in\n"
            "2. Click on 'Result' tab in the main menu\n"
            "3. Find 'SSC MTS & Havaldar 2024 Final Result'\n"
            "4. Download the PDF and use Ctrl+F to search your roll number"
        ),
        "google_search": "https://www.google.com/search?q=SSC+MTS+2026+Final+Result+latest+update",
    },
    "rrb_ntpc": {
        "name": "RRB NTPC Graduate 2026",
        "full_name": "RRB NTPC Graduate Level CEN 05/2024 (8113 Posts)",
        "icon": "🚂",
        "status": "released",
        "result_date": "2026-05-07",   # Final result declared 7 May 2026
        "result_link": "https://www.rrbapply.gov.in/",
        "description": (
            "RRB NTPC Graduate Level CEN 05/2024 Final Result declared on 7 May 2026. "
            "Zone-wise PDFs released for 8113 vacancies (Station Master, Goods Guard, "
            "Senior Clerk, JAA, etc.). Scorecards available till 22 May 2026."
        ),
        "steps": (
            "1. Visit your regional RRB website (e.g. rrbcdg.gov.in, rrbchennai.gov.in)\n"
            "2. Look for 'CEN 05/2024 NTPC-Graduate: Final Result'\n"
            "3. Download zone-wise PDF\n"
            "4. Use Ctrl+F to find your roll number\n"
            "5. Download scorecard via login with Registration No. & DOB"
        ),
        "google_search": "https://www.google.com/search?q=RRB+NTPC+Graduate+CEN+05+2024+Final+Result+latest",
    },
    "rrb_groupd": {
        "name": "RRB Group D 2026",
        "full_name": "RRB Group D CEN 08/2024 (32,438 Posts)",
        "icon": "🛤️",
        "status": "awaited",
        "result_date": None,           # Not yet released as of May 2026
        "result_link": "https://www.rrbapply.gov.in/",
        "description": (
            "RRB Group D CEN 08/2024 result is AWAITED. Exam was conducted from "
            "27 Nov 2025 to 10 Feb 2026. Result expected to be released soon on "
            "regional RRB websites. 32,438 vacancies for Track Maintainer, "
            "Assistant Pointsman, Helper/Assistant posts."
        ),
        "steps": (
            "1. Visit your regional RRB website\n"
            "2. Look for 'CEN 08/2024 Group D Result' link\n"
            "3. Download the CBT result PDF\n"
            "4. Search your roll number with Ctrl+F\n"
            "5. Qualified candidates called for PET next"
        ),
        "google_search": "https://www.google.com/search?q=RRB+Group+D+CEN+08+2024+Result+Date+latest+update+2026",
    },
}

# ─── LOGGING ─────────────────────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# ─── HELPERS ─────────────────────────────────────────────────────────────────

def check_today_alerts() -> list[str]:
    """Return list of exam names whose result was released today."""
    today = date.today().isoformat()
    alerts = []
    for exam in EXAMS.values():
        if exam["result_date"] == today:
            alerts.append(exam["name"])
    return alerts


def build_main_keyboard() -> InlineKeyboardMarkup:
    alerts = check_today_alerts()
    buttons = []
    for key, exam in EXAMS.items():
        label = f"{exam['icon']} {exam['name']}"
        if exam["name"] in alerts:
            label = "🔔 " + label + " — RESULT OUT TODAY!"
        buttons.append([InlineKeyboardButton(label, callback_data=key)])
    buttons.append([InlineKeyboardButton("🔍 Search Google for Latest News", callback_data="google_all")])
    return InlineKeyboardMarkup(buttons)


def format_result_message(key: str) -> str:
    exam = EXAMS[key]
    today_alerts = check_today_alerts()

    alert_banner = ""
    if exam["name"] in today_alerts:
        alert_banner = "🚨 *RESULT RELEASED TODAY!* 🚨\n\n"

    status_icon = "✅" if exam["status"] == "released" else "⏳"
    status_text = "DECLARED" if exam["status"] == "released" else "AWAITED / NOT YET RELEASED"

    result_date_text = (
        f"📅 *Result Date:* {exam['result_date']}"
        if exam["result_date"]
        else "📅 *Result Date:* Not announced yet"
    )

    msg = (
        f"{alert_banner}"
        f"{exam['icon']} *{exam['full_name']}*\n"
        f"{'─' * 35}\n\n"
        f"{status_icon} *Status:* {status_text}\n"
        f"{result_date_text}\n\n"
        f"📝 *Details:*\n{exam['description']}\n\n"
        f"📌 *How to Check:*\n{exam['steps']}\n\n"
        f"🌐 *Official Website:* {exam['result_link']}"
    )
    return msg


def build_exam_keyboard(key: str) -> InlineKeyboardMarkup:
    exam = EXAMS[key]
    buttons = [
        [InlineKeyboardButton("🌐 Open Official Website", url=exam["result_link"])],
        [InlineKeyboardButton("🔍 Google Latest Updates", url=exam["google_search"])],
        [InlineKeyboardButton("« Back to Exam List", callback_data="back_home")],
    ]
    return InlineKeyboardMarkup(buttons)


# ─── HANDLERS ────────────────────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    today_alerts = check_today_alerts()
    alert_text = ""
    if today_alerts:
        alert_text = (
            f"\n\n🚨 *ALERT: Result released TODAY for:*\n"
            + "\n".join(f"  • {name}" for name in today_alerts)
        )

    welcome = (
        f"👋 *Welcome to Exam Result Tracker Bot!*\n\n"
        f"Stay updated with the latest results for:\n"
        f"  📋 SSC MTS\n"
        f"  🚂 RRB NTPC\n"
        f"  🛤️ RRB Group D\n"
        f" Powered BY: Sakthi Kumaran☄️\n"
        f"{alert_text}\n\n"
        f"*Select an exam below to check its result status:*"
    )
    await update.message.reply_text(
        welcome,
        parse_mode="Markdown",
        reply_markup=build_main_keyboard(),
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == "back_home":
        today_alerts = check_today_alerts()
        alert_text = ""
        if today_alerts:
            alert_text = (
                f"\n\n🚨 *ALERT: Result released TODAY for:*\n"
                + "\n".join(f"  • {name}" for name in today_alerts)
            )
        text = f"*Select an exam to check result status:*{alert_text}"
        await query.edit_message_text(
            text,
            parse_mode="Markdown",
            reply_markup=build_main_keyboard(),
        )

    elif query.data == "google_all":
        await query.edit_message_text(
            "🔍 *Search for latest updates:*\n\n"
            "• [SSC MTS Latest Result](https://www.google.com/search?q=SSC+MTS+result+2026+latest)\n"
            "• [RRB NTPC Latest Result](https://www.google.com/search?q=RRB+NTPC+result+2026+latest)\n"
            "• [RRB Group D Latest Result](https://www.google.com/search?q=RRB+Group+D+result+2026+latest)\n\n"
            "Tap any link to search Google for the freshest updates.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("« Back", callback_data="back_home")]
            ]),
        )

    elif query.data in EXAMS:
        msg = format_result_message(query.data)
        keyboard = build_exam_keyboard(query.data)
        await query.edit_message_text(msg, parse_mode="Markdown", reply_markup=keyboard)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "ℹ️ *Bot Commands:*\n\n"
        "/start — Show exam list and result status\n"
        "/help  — Show this help message\n\n"
        "The bot automatically alerts you if any result was released today! 🔔",
        parse_mode="Markdown",
    )


# ─── SCHEDULED DAILY CHECK (optional) ───────────────────────────────────────
# Uncomment to push daily alerts to a specific chat.
#
# async def daily_check(context: ContextTypes.DEFAULT_TYPE) -> None:
#     alerts = check_today_alerts()
#     if alerts:
#         CHAT_ID = 8640224009 # Replace with your chat/group ID
#         msg = "🚨 *RESULT ALERT!*\n\nResult declared today for:\n" + \
#               "\n".join(f"  • {name}" for name in alerts)
#         await context.bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode="Markdown")
#
# In main(), add after app.build():
#   app.job_queue.run_daily(daily_check, time=datetime.time(hour=9, minute=0))


# ─── MAIN ────────────────────────────────────────────────────────────────────

def main() -> None:
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(button_handler))

    logger.info("Bot is running... Press Ctrl+C to stop.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
