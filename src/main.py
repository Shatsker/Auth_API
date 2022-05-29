import os

from flask import Flask
from flasgger import Swagger
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

from base.low_level import CacheRedis
from api.v1.users import user_router
from api.v1.auth import auth_router
from api.v1.roles import role_router
from db.postgres import init_db

load_dotenv()


def create_app():
    """Создание и инициализация приложения Flask."""
    app = Flask(__name__)
    app.config.from_pyfile(os.path.join('core', 'config.py'))

    swagger = Swagger(app)
    jwt = JWTManager(app)

    app.register_blueprint(user_router)
    app.register_blueprint(auth_router)
    app.register_blueprint(role_router)

    return app, swagger, jwt


def main(app):
    """Точка входа в приложение."""
    init_db()
    app.run(
        host=os.getenv('APP_HOST'),
        port=os.getenv('APP_PORT'),
        use_reloader=True,
    )


app, swagger, jwt = create_app()


@jwt.token_in_blocklist_loader
def check_if_token_was_in_logout_request(jwt_header: dict, jwt_payload: dict) -> bool:
    """Проверяет, был ли токен в запросе на логаут."""
    token_in_redis = CacheRedis().get_by_key(jwt_payload['jti'])
    return token_in_redis is not None


if __name__ == '__main__':
    main(
        app,
    )
