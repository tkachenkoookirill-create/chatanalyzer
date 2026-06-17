import asyncio
import logging
from datetime import datetime, timezone
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

import config
from reader import fetch_all_groups
from analyzer import analyze_messages
from reporter import send_report

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger(__name__)


async def run_report_job(lookback_hours: int):
    log.info(f"Starting report job (lookback={lookback_hours}h)...")
    try:
        raw = await fetch_all_groups(hours_back=lookback_hours)

        analyzed = {}
        for group, messages in raw.items():
            if isinstance(messages, dict) and "error" in messages:
                analyzed[group] = messages
            else:
                log.info(f"Analyzing {len(messages)} messages from {group}")
                analyzed[group] = analyze_messages(messages, group)

        await send_report(analyzed)
        log.info("Report sent successfully.")
    except Exception as e:
        log.error(f"Report job failed: {e}", exc_info=True)


def main():
    if not config.API_ID or not config.BOT_TOKEN or not config.MONITOR_GROUPS:
        log.error("Missing required config. Check your .env file.")
        return

    scheduler = AsyncIOScheduler(timezone="UTC")

    for window in config.SCHEDULE_WINDOWS:
        hour, minute = map(int, window["utc_time"].split(":"))
        scheduler.add_job(
            run_report_job,
            CronTrigger(hour=hour, minute=minute),
            kwargs={"lookback_hours": window["lookback_hours"]},
            id=f"report_{window['utc_time']}",
            name=f"Report at {window['utc_time']} UTC",
            replace_existing=True,
        )
        log.info(f"Scheduled report at {window['utc_time']} UTC (lookback={window['lookback_hours']}h)")

    scheduler.start()
    log.info("Scheduler started. Waiting for jobs...")

    loop = asyncio.get_event_loop()
    try:
        loop.run_forever()
    except (KeyboardInterrupt, SystemExit):
        log.info("Shutting down...")
        scheduler.shutdown()


if __name__ == "__main__":
    main()
