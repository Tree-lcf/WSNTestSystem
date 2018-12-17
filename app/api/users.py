from app.api import bp
from flask import request
from app.models import *
from app.auth.auth import verify_token, token_auth_error
from app.errors import trueReturn


@bp.before_request
def before_request():
    token = request.cookies.get('token')
    if not verify_token(token):
        return token_auth_error()


@bp.route('/users', methods=['GET'])
def get_users():
    # page_num = request.args.get('page_num', 1, type=int)
    # per_page = request.args.get('per_page', 10, type=int)
    users = User.to_collection_dict()
    response = trueReturn(users, 'success')
    return response
