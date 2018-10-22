from flask import jsonify
from werkzeug.http import HTTP_STATUS_CODES


def error_response(status_code, message=None):
    payload = {'error': HTTP_STATUS_CODES.get(status_code, 'Unknown error'), 'status': False, 'message': message}
    response = jsonify(payload)
    response.status_code = status_code
    return response


def bad_request(message):
    return error_response(400, message)


def trueReturn(data=None, message=None):
    payload = {
        "status": True,
        "data": data,
        "msg": message
    }
    response = jsonify(payload)
    return response
