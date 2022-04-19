import os

from flask import Flask
from flasgger import Swagger
from dotenv import load_dotenv

from api.v1.users import user_router
from db.postgres import init_db


load_dotenv()

app = Flask(__name__)
app.register_blueprint(user_router)

swagger = Swagger(app)


def main():
    init_db()
    app.run(
        host=os.getenv('APP_HOST'),
        port=os.getenv('APP_PORT'),
        use_reloader=True,
    )


if __name__ == '__main__':
    main()

