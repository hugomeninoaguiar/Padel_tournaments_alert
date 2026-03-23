import asyncio
import logging
import os

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

import database
from main import run_check

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

TIMEZONE = "Europe/Lisbon"
BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]

HELP_TEXT = """🎾 *Padel Tournament Alert Bot*

Monitoring the Portuguese Padel Federation calendar for new tournaments.

*What it tracks:*
– ABS (Absolutos) tournaments only
– Current month + next month
– Future tournaments only (past ones are ignored)

*When it checks:*
– Every day at 10:00 and 16:00 (Lisbon time)

*When you get notified:*
– Only when a genuinely new tournament appears that wasn't listed before
– No news = no message (silence is good news)

*What a notification looks like:*
🆕 1 novo torneio encontrado!

🎾 *Tournament Name*
💰 5.000 ABS
📅 25 Mar - 29 Mar
📍 Venue Name
🏷 Masculinos 1, Femininos 1, ...
🔗 https://fpp.tiepadel.com/...

*Commands:*
/help – show this message
/status – show tournaments stored in the database
"""


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(HELP_TEXT, parse_mode="Markdown")


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    database.init_db()
    tournaments = database.get_all()
    count = len(tournaments)
    if count == 0:
        await update.message.reply_text("No tournaments in the database yet.")
        return

    lines = [f"*{count} tournaments stored:*\n"]
    for t in tournaments[:10]:
        lines.append(f"• {t['name']} — {t['date']}")
    if count > 10:
        lines.append(f"_...and {count - 10} more_")

    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


async def main() -> None:
    # Set up telegram bot for /help command
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("status", status_command))

    # Set up scheduler
    scheduler = AsyncIOScheduler(timezone=TIMEZONE)
    scheduler.add_job(run_check, CronTrigger(hour=10, minute=0, timezone=TIMEZONE))
    scheduler.add_job(run_check, CronTrigger(hour=16, minute=0, timezone=TIMEZONE))

    async with app:
        await app.start()
        await app.updater.start_polling()
        scheduler.start()
        log.info("Scheduler started. Runs at 10:00 and 16:00 (%s).", TIMEZONE)
        log.info("Bot polling started. /help is active.")

        try:
            await asyncio.Event().wait()  # run forever
        except (KeyboardInterrupt, SystemExit):
            pass
        finally:
            scheduler.shutdown()
            await app.updater.stop()
            await app.stop()
            log.info("Stopped.")


if __name__ == "__main__":
    asyncio.run(main())
