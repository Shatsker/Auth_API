import os

from flask import Flask
from flasgger import Swagger
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

from api.v1.users import user_router
from api.v1.auth import auth_router
from db.postgres import init_db
from core import config


load_dotenv()

app = Flask(__name__)
app.register_blueprint(user_router)
app.register_blueprint(auth_router)
app.config['JWT_SECRET_KEY'] = config.JWT_SECRET_KEY
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = config.JWT_ACCESS_TOKEN_EXPIRES
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = config.JWT_REFRESH_TOKEN_EXPIRES

swagger = Swagger(app)
jwt = JWTManager(app)


def main():
    init_db()
    app.run(
        host=os.getenv('APP_HOST'),
        port=os.getenv('APP_PORT'),
        use_reloader=True,
    )


if __name__ == '__main__':
    main()

