import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from main import run_check

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

TIMEZONE = "Europe/Lisbon"


async def main() -> None:
    scheduler = AsyncIOScheduler(timezone=TIMEZONE)
    scheduler.add_job(run_check, CronTrigger(hour=10, minute=0, timezone=TIMEZONE))
    scheduler.add_job(run_check, CronTrigger(hour=16, minute=0, timezone=TIMEZONE))
    scheduler.start()
    log.info("Scheduler started. Runs at 10:00 and 16:00 (%s).", TIMEZONE)

    try:
        await asyncio.Event().wait()  # run forever
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        log.info("Scheduler stopped.")


if __name__ == "__main__":
    asyncio.run(main())
