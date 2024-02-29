import os

from dotenv import load_dotenv
load_dotenv()

class Config:
    def __init__(self):
        self.RESY_USER_CONFIG = os.getenv("RESY_USER_CONFIG")
        self.SLACK_URL = os.getenv("SLACK_URL")
        self.RESERVATION_CONFIG_PATH = os.getenv("RESERVATION_CONFIG_PATH")