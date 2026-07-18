import logging
import os
import threading
from datetime import time as dt_time
from zoneinfo import ZoneInfo

from flask import Flask

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes
)

from config import (
    BOT_TOKEN,
    CHAT_ID,
    TIMEZONE,
    SEND_TIME,
    FOOTER
)

from data import get_all_market_data


# ==========================================================
# LOGGING
# ==========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


# ==========================================================
# FLASK WEB SERVER
# ==========================================================

web_app = Flask(__name__)


@web_app.route("/")
def home():

    return "ParthTraderAlerts Pivot Bot is Running!"


@web_app.route("/health")
def health():

    return "OK"


def run_web_server():

    port = int(
        os.environ.get(
            "PORT",
            10000
        )
    )

    web_app.run(
        host="0.0.0.0",
        port=port
    )


# ==========================================================
# CREATE PIVOT MESSAGE
# ==========================================================

def create_pivot_message():

    market_data = get_all_market_data()

    if not market_data:

        return (
            "⚠️ <b>ParthTraderAlerts</b>\n\n"
            "❌ Market data unavailable.\n"
            "Please try again later."
        )

    message = (
        "📊 <b>ParthTraderAlerts</b>\n\n"
        "🕘 <b>Daily Pivot Levels</b>\n"
        "🇮🇳 Indian Market\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
    )

    for name, data in market_data.items():

        pivot = data["pivot"]
        cpr = data["cpr"]

        message += (
            f"📈 <b>{name}</b>\n"
            f"📅 Data Date: {data['date']}\n\n"

            f"🔺 High: {data['high']}\n"
            f"🔻 Low: {data['low']}\n"
            f"🔹 Close: {data['close']}\n\n"

            f"🟡 <b>PIVOT: {pivot['Pivot']}</b>\n\n"

            f"🟢 R1: {pivot['R1']}\n"
            f"🟢 R2: {pivot['R2']}\n"
            f"🟢 R3: {pivot['R3']}\n\n"

            f"🔴 S1: {pivot['S1']}\n"
            f"🔴 S2: {pivot['S2']}\n"
            f"🔴 S3: {pivot['S3']}\n\n"

            f"📊 <b>CPR</b>\n"
            f"TC: {cpr['TC']}\n"
            f"BC: {cpr['BC']}\n\n"

            "━━━━━━━━━━━━━━━━━━\n\n"
        )

    message += (
        "🚀 Trade With Discipline\n\n"
        f"{FOOTER}"
    )

    return message


# ==========================================================
# AUTOMATIC DAILY PIVOT MESSAGE
# ==========================================================

async def send_pivot_message(
    context: ContextTypes.DEFAULT_TYPE
):

    try:

        message = create_pivot_message()

        await context.bot.send_message(
            chat_id=CHAT_ID,
            text=message,
            parse_mode="HTML"
        )

        logging.info(
            "Daily Pivot message sent successfully"
        )

    except Exception as error:

        logging.error(
            f"Telegram send error: {error}"
        )


# ==========================================================
# /START COMMAND
# ==========================================================

async def start_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        "🤖 <b>ParthTraderAlerts Pivot Bot</b>\n\n"
        "✅ Bot is active.\n\n"
        "Use /pivot to get Pivot Levels.",
        parse_mode="HTML"
    )


# ==========================================================
# /PIVOT COMMAND
# ==========================================================

async def pivot_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    message = create_pivot_message()

    await update.message.reply_text(
        message,
        parse_mode="HTML"
    )


# ==========================================================
# /HELP COMMAND
# ==========================================================

async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        "📊 <b>ParthTraderAlerts Pivot Bot</b>\n\n"
        "/start - Start Bot\n"
        "/pivot - Get Pivot Levels\n"
        "/help - Show Help\n\n"
        "⏰ Daily automatic update: 09:15 AM IST",
        parse_mode="HTML"
    )


# ==========================================================
# MAIN
# ==========================================================

def main():

    if not BOT_TOKEN:

        raise ValueError(
            "BOT_TOKEN environment variable is missing"
        )

    if not CHAT_ID:

        raise ValueError(
            "CHAT_ID environment variable is missing"
        )


    # Start Flask Web Server
    web_thread = threading.Thread(
        target=run_web_server,
        daemon=True
    )

    web_thread.start()


    # Create Telegram Application
    app = (
        Application
        .builder()
        .token(BOT_TOKEN)
        .build()
    )


    # Telegram Commands
    app.add_handler(
        CommandHandler(
            "start",
            start_command
        )
    )

    app.add_handler(
        CommandHandler(
            "pivot",
            pivot_command
        )
    )

    app.add_handler(
        CommandHandler(
            "help",
            help_command
        )
    )


    # Daily Schedule
    hour, minute = map(
        int,
        SEND_TIME.split(":")
    )


    app.job_queue.run_daily(
        send_pivot_message,
        time=dt_time(
            hour=hour,
            minute=minute,
            tzinfo=ZoneInfo(TIMEZONE)
        ),
        name="daily_pivot_update"
    )


    logging.info(
        "ParthTraderAlerts Pivot Bot Started"
    )

    logging.info(
        "Daily Schedule: 09:15 AM IST"
    )


    # Start Telegram Bot
    import asyncio

    asyncio.set_event_loop(
        asyncio.new_event_loop()
    )

    app.run_polling()


# ==========================================================
# RUN
# ==========================================================

if __name__ == "__main__":

    main()
