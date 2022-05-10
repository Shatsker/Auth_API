import os

from redis import Redis
from dotenv import load_dotenv


load_dotenv()

redis_db = Redis(
    host=os.getenv('REDIS_HOST'),
    port=int(os.getenv('REDIS_PORT')),
    db=int(os.getenv('REDIS_DB')),
)
