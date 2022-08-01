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

YANDEX_CLIENT_ID = os.getenv('YANDEX_CLIENT_ID')
YANDEX_CLIENT_SECRET = os.getenv('YANDEX_CLIENT_SECRET')
YANDEX_NAME = os.getenv('YANDEX_NAME')
YANDEX_AUTHORIZE_URL = os.getenv('YANDEX_AUTHORIZE_URL')
YANDEX_ACCESS_TOKEN_URL = os.getenv('YANDEX_ACCESS_TOKEN_URL')
YANDEX_BASE_URL = os.getenv('YANDEX_BASE_URL')
YANDEX_REDIRECT_URI = os.getenv('YANDEX_REDIRECT_URI')
