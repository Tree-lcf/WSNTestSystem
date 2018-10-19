from flask import g
from app.models import User
from app.errors import error_response


def verify_password(username, password):
    user = User.query.filter_by(username=username).first()
    if user is None:
        return False
    g.current_user = user
    return user.check_password(password)


def basic_auth_error():
    return error_response(401, '授权失败，用户名或密码错误')


def verify_token(token):
    g.current_user = User.check_token(token) if token else None
    return g.current_user is not None


def token_auth_error():
    return error_response(401, '授权无效或授权过期，请重新登录')
