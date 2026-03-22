# Padel Tournament Alert

Monitors the Portuguese Padel/Tennis Federation tournament calendar and sends a Telegram notification whenever a new tournament appears.

## How It Works

Runs twice a day (10:00 and 16:00 Lisbon time). Scrapes the current and next month from [tour.tiesports.com](https://tour.tiesports.com/fpp/calendar_(tournaments)) using Playwright, compares against a local SQLite database, and sends a Telegram message for any new entries.

## Local Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. Create a Telegram bot

1. Open Telegram and message `@BotFather`
2. Send `/newbot` and follow the prompts
3. Copy the bot token you receive

### 3. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` with your values:
- `TELEGRAM_BOT_TOKEN` — the token from BotFather
- `TELEGRAM_CHAT_ID` — your Telegram chat ID (same as your other bots)

### 4. Run manually

```bash
python main.py
```

- **First run**: scrapes and stores all tournaments silently (no notification sent — avoids spam)
- **Subsequent runs**: only notifies about genuinely new tournaments

### 5. Start the scheduler

```bash
python scheduler.py
```

## Railway Deployment

Add this as a **new service** inside your existing Railway project:

1. In your Railway project, click **+ New Service → GitHub Repo** (or deploy from this folder)
2. Railway will detect the `Dockerfile` automatically
3. Set the environment variables in the Railway service settings:
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
4. Deploy — the scheduler starts automatically and runs forever

The SQLite database (`tournaments.db`) is stored inside the container. To persist it across Railway deploys, attach a Railway Volume and set `DB_PATH` to a path within that volume (or mount it at `/data/tournaments.db`).

## Project Structure

| File | Purpose |
|------|---------|
| `main.py` | Entry point for a single check cycle; use for manual testing |
| `scheduler.py` | Production entry point; runs `main.py` at 10:00 and 16:00 |
| `scraper.py` | Playwright browser automation against tour.tiesports.com |
| `database.py` | SQLite read/write and deduplication logic |
| `notifier.py` | Telegram message formatting and sending |
