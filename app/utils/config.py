import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    APP_USER_EMAIL = os.environ.get("APP_USER_EMAIL")
    APP_USER_PASSWORD = os.environ.get("APP_USER_PASSWORD")

    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        hours=int(os.environ.get("JWT_ACCESS_TOKEN_EXPIRES", 6))
    )

    AWS_REGION = os.environ.get("AWS_REGION")
    SQS_MAIN_QUEUE = os.environ.get("SQS_MAIN_QUEUE")