import os

from dotenv import load_dotenv


load_dotenv()

APP_HOST = os.getenv('APP_HOST', '0.0.0.0')
APP_PORT = os.getenv('APP_PORT', 8000)
