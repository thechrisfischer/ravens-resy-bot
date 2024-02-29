import json

from apscheduler.schedulers.background import BackgroundScheduler
from resy_bot.logging import logging, Slogger
from resy_bot.models import ResyConfig, TimedReservationRequest
from resy_bot.manager import ResyManager

from config import Config

config = Config()

RESY_USER_CONFIG = config.RESY_USER_CONFIG
RESERVATION_CONFIG_PATH = config.RESERVATION_CONFIG_PATH

logger = logging.getLogger("Scheduler")
logger.setLevel("INFO")

slogger = Slogger()

scheduler = BackgroundScheduler(logger=logger, timezone='America/New_York')
scheduler.start()

def get_scheduled_jobs():
    jobs = scheduler.get_jobs()

    for j in jobs:
        print(f"{j.id} ---- {j.next_run_time}")
    return

def load_reservations() -> None:
    logger.info("loading reservation requests")
    
    config_data = json.loads(RESY_USER_CONFIG)

    with open(RESERVATION_CONFIG_PATH, "r") as f:
        reservation_data = json.load(f)

    config = ResyConfig(**config_data)
    manager = ResyManager.build(config)

    scheduled_reservations = reservation_data["scheduled"]
    restaurants = scheduled_reservations.keys()
    job_ids = []
    for r in restaurants:
        reservation_request = scheduled_reservations[r]
        logger.info(reservation_request)
        logger.info(f"Making a scheduled reservation drop for {reservation_request}")
        timed_request = TimedReservationRequest(**reservation_request)
        scheduler.add_job(manager.make_reservation_at_opening_time, args=[timed_request], trigger="cron", hour="7", id=r, replace_existing=True)
        job_ids.append(r)
    
    return


if __name__ == "__main__":

    ###load_reservations()
    scheduler.add_job(get_scheduled_jobs, "interval", minutes=1)