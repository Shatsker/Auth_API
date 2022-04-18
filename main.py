import os

from flask import Flask
from flasgger import Swagger
from dotenv import load_dotenv


load_dotenv()

app = Flask(__name__)
swagger = Swagger(app)


if __name__ == '__main__':
    app.run(
        host=os.getenv('APP_HOST'),
        port=os.getenv('APP_PORT'),
    )
