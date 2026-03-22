import asyncio
import logging

import database
import notifier
import scraper

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)


async def run_check() -> None:
    database.init_db()

    log.info("Starting tournament check...")
    try:
        tournaments = await scraper.scrape_tournaments()
    except Exception as e:
        log.error("Scraper failed: %s", e)
        await notifier.send_error(str(e))
        return

    log.info("Scraped %d tournaments", len(tournaments))

    if database.is_first_run():
        database.add_tournaments(tournaments)
        log.info("First run — stored %d tournaments, no notifications sent.", len(tournaments))
        return

    new_tournaments = database.filter_new(tournaments)
    log.info("Found %d new tournaments", len(new_tournaments))

    if new_tournaments:
        database.add_tournaments(new_tournaments)
        await notifier.send_new_tournaments(new_tournaments)
        log.info("Notification sent.")
    else:
        log.info("No new tournaments. Nothing to send.")


if __name__ == "__main__":
    asyncio.run(run_check())
