import os
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()

APP_HOST = os.getenv('APP_HOST', '0.0.0.0')
APP_PORT = os.getenv('APP_PORT', 8000)

JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=4)
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=1)

PREFIX_FOR_ACCESS_TOKEN = 'access'
PREFIX_FOR_REFRESH_TOKEN = 'refresh'
