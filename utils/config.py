import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL", "https://dev.labs.wonk.study")

ACCOUNT_1_USERNAME = os.getenv("ACCOUNT_1_USERNAME")
ACCOUNT_1_PASSWORD = os.getenv("ACCOUNT_1_PASSWORD")
