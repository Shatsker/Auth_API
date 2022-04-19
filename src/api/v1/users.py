from flask import Blueprint

from models.users import User
from schemas.users import UserSchema


user_router = Blueprint('user_router', __name__)


@user_router.route('/api/v1/users')
def get_users():
    """Получение всех юзеров."""
    users = User.query.all()
    return UserSchema(many=True).dumps(users)
