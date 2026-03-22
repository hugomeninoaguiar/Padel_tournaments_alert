PROJECT: Tennis Tournament Monitor for Hugo
What We Are Building
A personal monitor that checks the Portuguese Padel/Tennis Federation tournament calendar twice a day and sends Hugo a Telegram notification whenever a new tournament appears that he can register for. Hugo plays padel and wants to know about new tournaments as soon as they are listed.

Tech Stack
Python. Playwright for browser automation and scraping since the site likely renders content via JavaScript. APScheduler for running twice a day. SQLite for tracking tournaments already seen. python-telegram-bot for Telegram notifications. python-dotenv for environment variables. Everything should work locally first then deploy to Railway.

The Website
URL is https://tour.tiesports.com/fpp/calendar_(tournaments)
The page has filters for year, month, escalão and tipo. It requires clicking a Filtrar button to load results. No login required. The scraper should always check two months: the current month and the next month, both dynamically calculated so it never needs manual updating.

How It Works
Step 1 is the scheduled trigger. Runs twice a day, once in the morning around 10am and once in the evening around 4pm. Locally triggerable manually for testing.
Step 2 is scraping. Use Playwright to open the page. Set the year filter to current year. Set the month filter to current month. Click Filtrar. Wait for results to load. Scrape all tournaments listed. Repeat for next month. Each tournament should capture the name, date, location, escalões available and any other visible details.
Step 3 is comparison. Compare scraped tournaments against the SQLite database of tournaments already seen. Identify any that are new, meaning not in the database yet. Add all new ones to the database with the date they were first seen.
Step 4 is Telegram notification. If new tournaments were found send Hugo a Telegram message with the details of each new tournament. Include the name, date, location and escalões. If no new tournaments were found send nothing, no need to message if there is nothing new.

Telegram
Create a new bot via BotFather. The TELEGRAM_CHAT_ID is the same as Hugo uses for other bots. Only the bot token is different.

State Tracking
Use SQLite to store every tournament ever seen. Store the tournament name, date, location, escalões, the URL or unique identifier if available, and the date it was first detected. On each run compare the full scraped list against the database. Only notify about genuinely new entries never seen before.

Environment Variables
TELEGRAM_BOT_TOKEN for this specific padel bot. TELEGRAM_CHAT_ID for Hugo's Telegram chat ID. No API keys needed since there is no AI step in this workflow.

Project Structure
A scraper module that handles Playwright browser automation and tournament extraction for current and next month. A database module that handles SQLite operations for storing and checking tournaments. A notifier module that handles Telegram message formatting and sending. A scheduler that runs the full check twice a day. A main script that ties everything together and is also manually runnable for testing. A .env template. A requirements.txt. A README with setup instructions for Playwright, Telegram bot setup and Railway deployment.

Local Testing
The scraper should be runnable manually to test it works before the scheduler is involved. On first run it will scrape everything and store it all as seen without sending notifications, since everything would be new and that would be noisy. From the second run onwards only genuinely new tournaments trigger a notification. Add a flag like first_run detection to handle this gracefully.

Edge Cases
If the page fails to load or Playwright times out send Hugo a Telegram message saying the check failed so he knows. If the filters do not respond as expected log the error clearly. Handle the month rollover correctly, in December the next month is January of the next year. If a tournament changes details but has the same name treat it as the same tournament unless the date also changes.
What Not to Build
No web interface. No AI step needed for this, it is simple enough without Claude. Keep it as simple as possible.

We will use python and Railways to have the service runing there as we already have one there. Tell us if it is a differenty project or the same project we have there but with another serrvice. What is better we have on project with already a bot telegram.