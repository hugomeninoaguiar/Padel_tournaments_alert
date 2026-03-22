# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt
playwright install chromium

# Run a single check cycle manually (use for testing)
python main.py

# Start the production scheduler (10:00 and 16:00 Lisbon time)
python scheduler.py
```

## Architecture

Five modules, no framework:

- **[main.py](main.py)** — orchestrates one full check cycle: scrape → compare → store → notify. Also the manual test entry point (`python main.py`).
- **[scraper.py](scraper.py)** — async Playwright scraper. Always checks two months (current + next, with December→January year rollover). Returns a list of tournament dicts with keys: `name`, `date`, `location`, `escaloes`, `url`.
- **[database.py](database.py)** — SQLite (`tournaments.db`). Tournament IDs are a 16-char SHA-256 hash of `name|date`. Key logic: `is_first_run()` (table empty check), `filter_new()` (returns only tournaments not yet in DB).
- **[notifier.py](notifier.py)** — sends Telegram messages via `python-telegram-bot`. Two functions: `send_new_tournaments()` and `send_error()`.
- **[scheduler.py](scheduler.py)** — `APScheduler` `AsyncIOScheduler` that calls `run_check()` twice daily. Production entry point.

## First-Run Behaviour

On first run, all scraped tournaments are stored silently — no Telegram notification is sent. This prevents a spam burst on initial deployment. From the second run onward, only genuinely new entries trigger a notification.

## Environment Variables

Required in `.env` (copy from `.env.example`):
- `TELEGRAM_BOT_TOKEN` — token for this specific padel bot (from BotFather)
- `TELEGRAM_CHAT_ID` — Hugo's Telegram chat ID

## Railway Deployment

Deploy as a **new service** inside the existing Railway project. Railway detects the `Dockerfile` automatically. Set `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` as Railway environment variables. The `CMD` is `python scheduler.py`.

SQLite is stored inside the container at `tournaments.db`. For persistence across Railway deploys, attach a Railway Volume and point `DB_PATH` in [database.py](database.py) to a path within it.
