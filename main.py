import json
import dateparser
import datetime
import os

from config import Config

from resy_bot.logging import logging, Slogger
from resy_bot.models import ResyConfig, TimedReservationRequest, WaitlistReservationRequest
from resy_bot.manager import ResyManager

from flask import Flask, request, Response, render_template

config = Config()

RESY_USER_CONFIG = config.RESY_USER_CONFIG
RESERVATION_CONFIG_PATH = config.RESERVATION_CONFIG_PATH

logger = logging.getLogger(__name__)
logger.setLevel("INFO")

app = Flask(__name__)

slogger = Slogger()

def get_waitlisted_table(resy_config_path: str, reservation_config_path: str, 
                         notification):
    
    logger.info("Looking for a reservation from incoming webhook")

    config_data = json.loads(RESY_USER_CONFIG)

    with open(reservation_config_path, "r") as f:
        reservation_config = json.load(f)

    venue_name = notification[0].lower().replace(" ", "_")
    reservation_request = reservation_config["waitlisted"][venue_name]
    ideal_date = dateparser.parse(notification[1])
    party_size = int(notification[2].strip(" Guests"))
    
    reservation_request["reservation_request"]["ideal_date"] = ideal_date
    reservation_request["reservation_request"]["party_size"] = party_size

    config = ResyConfig(**config_data)
    manager = ResyManager.build(config)

    slogger.slog(f"We've got a live one, making a request for {venue_name} on {ideal_date} for {party_size} -- fingers crossed!")
    ### Make request
    waitlist_request = WaitlistReservationRequest(**reservation_request)

    logger.info(waitlist_request)
    return manager.make_reservation_now(waitlist_request)

### Routes for Flask app
@app.route('/table-notification', methods=['POST'])
def respond():
    notification = request.json["available_table"]
    data = notification.split("|")
    notification = [x.strip(" \n") for x in data]
    
    get_waitlisted_table(RESY_USER_CONFIG, RESERVATION_CONFIG_PATH, notification)
    return Response(status=200)

###@app.route('/scheduled-jobs')
###def get_scheduled_jobs():
###    jobs = scheduler.get_jobs()
###
###    for j in jobs:
###        print(f"{j.id} ---- {j.next_run_time}")
###        
###    return render_template("index.html", jobs=scheduler.get_jobs())

if __name__ == "__main__":

    app.run(debug = True, host = "0.0.0.0", port = 3000)