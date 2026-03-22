import os

from dotenv import load_dotenv
from telegram import Bot

load_dotenv()

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]


def _format_tournament(t: dict) -> str:
    lines = [f"🎾 *{t['name']}*"]
    if t.get("category"):
        lines.append(f"💰 {t['category']}")
    if t.get("date"):
        lines.append(f"📅 {t['date']}")
    if t.get("location"):
        lines.append(f"📍 {t['location']}")
    if t.get("escaloes"):
        lines.append(f"🏷 {t['escaloes']}")
    if t.get("url"):
        lines.append(f"🔗 {t['url']}")
    return "\n".join(lines)


async def send_new_tournaments(tournaments: list[dict]) -> None:
    bot = Bot(token=BOT_TOKEN)
    count = len(tournaments)
    header = f"🆕 {count} novo{'s' if count > 1 else ''} torneio{'s' if count > 1 else ''} encontrado{'s' if count > 1 else ''}!\n"
    body = "\n\n".join(_format_tournament(t) for t in tournaments)
    message = header + "\n" + body
    await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="Markdown")


async def send_error(error_message: str) -> None:
    bot = Bot(token=BOT_TOKEN)
    await bot.send_message(
        chat_id=CHAT_ID,
        text=f"⚠️ Padel monitor falhou:\n{error_message}",
    )
