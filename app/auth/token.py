from flask import jsonify, g
from app import db


def get_token():
    token = g.current_user.get_token()
    db.session.commit()
    data = {'token': token}
    return data


def revoke_token():
    g.current_user.revoke_token()
    db.session.commit()
    return '', 204
