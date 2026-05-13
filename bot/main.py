import logging
from datetime import date, datetime, time
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    JobQueue,
)
import requests
from bs4 import BeautifulSoup

BOT_TOKEN = "8640224009:AAGr1DPdJVLnsLK5hLNsNKlzF8AdEyzxgbc"
CHAT_ID = "8640224009"  # Replace with your chat/group ID to receive alerts
GOOGLE_API_KEY = "8bf6d1dea7604b57c68fa6c8b4bd8991785c582f2190f77f20fb758268c2428e"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

EXAMS = {
    "rrb_ntpc_062025": {
        "name": "RRB NTPC CEN 06/2025",
        "official_links": [
            "https://indianrailways.gov.in/notice/results",
            "https://www.rrbexamresults.gov.in",
        ],
        "result_date": "2026-05-07",
    },
    "rrb_groupd_082024": {
        "name": "RRB Group D CEN 08/2024",
        "official_links": [
            "https://indianrailways.gov.in/notice/results",
            "https://www.rrbgroupdresults.gov.in",
        ],
        "result_date": None,
    },
    "ssc_mts_feb2026": {
        "name": "SSC MTS Feb 2026",
        "official_links": [
            "https://ssc.nic.in/Results",
        ],
        "result_date": "2026-02-28",
    },
}

def get_official_result_text(url):
    try:
        r = requests.get(url, timeout=8)
        soup = BeautifulSoup(r.text, "html.parser")
        return soup.get_text(separator="\n")
    except Exception:
        return ""

def is_result_today(result_date_str):
    if not result_date_str:
        return False
    try:
        result_date = datetime.strptime(result_date_str, "%Y-%m-%d").date()
        return result_date == date.today()
    except Exception:
        return False

def build_exam_keyboard():
    buttons = []
    for key, exam in EXAMS.items():
        label = exam["name"]
        if is_result_today(exam["result_date"]):
            label = "🔔 " + label + " — RESULT OUT TODAY!"
        emoji = "🚂" if "ntpc" in key else "🛤️" if "groupd" in key else "📋"
        buttons.append([InlineKeyboardButton(f"{emoji} {label}", callback_data=key)])
    return InlineKeyboardMarkup(buttons)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_msg = (
        "👋 *Welcome to Exam Result Tracker Bot!* \n\n"
        "Select an exam below to check the latest result:\n"
        "----------------------------------------"
    )
    await update.message.reply_text(
        welcome_msg, parse_mode="Markdown", reply_markup=build_exam_keyboard()
    )

async def send_daily_alert(context: ContextTypes.DEFAULT_TYPE):
    alerts = []
    for exam in EXAMS.values():
        if is_result_today(exam["result_date"]):
            alerts.append(f"🔔 {exam['name']} — Result Released Today!")
    if alerts:
        msg = "🚨 *RESULT ALERT!* 🚨\n\n" + "\n".join(alerts)
        await context.bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode="Markdown")

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data

    if data == "back_home":
        await query.answer()
        await query.edit_message_text(
            "Select an exam to check the latest result:\n----------------------------------------",
            parse_mode="Markdown",
            reply_markup=build_exam_keyboard(),
        )
        return

    exam = EXAMS.get(data)
    if not exam:
        return
    await query.answer()

    result_date_line = f"📅 Result Date: {exam['result_date'] or 'Awaited'}\n\n"
    if is_result_today(exam["result_date"]):
        result_date_line = "🔔 " + result_date_line + " — *Released Today!*\n\n"

    txt = f"🎯 **{exam['name']} Results:**\n\n{result_date_line}"

    double_checked_text = ""
    for link in exam["official_links"]:
        text = get_official_result_text(link)
        snippet = "\n".join(line for line in text.split("\n") if exam['name'].split()[0].lower() in line.lower())[:7]
        double_checked_text += f"✅ Official ({link}):\n{snippet}\n\n"
    txt += double_checked_text.strip() or "⚠️ No result found on official sites.\n\n"

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Back to Exam List", callback_data="back_home")]
    ])
    await query.edit_message_text(txt, parse_mode="Markdown", reply_markup=keyboard)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))

    # Schedule daily alert at 9:00 AM
    job_queue: JobQueue = app.job_queue
    job_queue.run_daily(send_daily_alert, time=time(hour=9, minute=0))

    app.run_polling()

if __name__ == "__main__":
    main()
