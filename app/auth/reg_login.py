from flask import jsonify, request, g
from app.models import User
from app.auth import bp
from .token import get_token
from .auth import verify_password, basic_auth_error, verify_token, token_auth_error
from app.errors import bad_request, trueReturn
from app.common import session_commit


@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    if 'username' not in data or 'email' not in data or 'password' not in data:
        return bad_request('must include username, email and password fields')
    if User.query.filter_by(username=data['username']).first():
        return bad_request('please use a different username')
    if User.query.filter_by(email=data['email']).first():
        return bad_request('please use a different email address')
    user = User()
    user.from_dict(data)
    user.add()
    session_commit()
    if user.id:
        data = user.to_dict()
        response = trueReturn(data, '用户注册成功')
        # response.status_code = 201
        return response
    else:
        return bad_request('用户注册失败')


@bp.route('/login', methods=['POST'])
def login():
    # if g.current_user:
    #     data = g.current_user.to_dict()
    #     response = trueReturn(data, '用户已登录')
    #     return response
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return bad_request('must include username or password')
    # user = User.query.filter_by(username=username).first()
    # if user is None or not user.check_password(password):
    #     return bad_request('Invalid username or password')
    if verify_password(username, password):
        data = get_token()
        data['username'] = username
        return trueReturn(data, '登录成功')
    else:
        return basic_auth_error()


@bp.route('/logout', methods=['GET'])
def logout():
    token = request.cookies.get('token')
    if not verify_token(token):
        return token_auth_error()
    g.current_user.revoke_token()
    response = trueReturn(message='登出成功')
    return response
