from app.api import bp
from flask import jsonify, request, g
from app.models import *
from app.auth.auth import verify_token, token_auth_error
from app.errors import trueReturn


@bp.before_request
def before_request():
    token = request.cookies.get('token')
    print(token)
    if not verify_token(token):
        return token_auth_error()


@bp.route('/projects', methods=['GET'])
def get_projects():
    pageNum = request.args.get('pageNum', 1, type=int)
    perPage = request.args.get('perPage', 10, type=int)
    projects = g.current_user.projects.paginate(pageNum, perPage, False)
    project_namelist = [project.project_name if project else '' for project in projects.items]

    data = {
        'project_namelist': project_namelist,
        'has_next': projects.has_next,
        'next_num': projects.next_num,
        'has_prev': projects.has_prev,
        'prev_num': projects.prev_num
    }

    response = trueReturn(data, '请求成功')
    return response

#
# @bp.route('/api', methods=['GET'])
# def get_apis():
#     projects = Project.
#

# @bp.route('/api/<project_id>/<module_id>', methods=['GET'])
# def get_user(id):
#     pass
#
#
# @bp.route('/user/<int:id>/followers', methods=['GET'])
# def get_followers(id):
#     pass
#
# @bp.route('/user/<int:id>/followed', methods=['GET'])
# def get_followed(id):
#     pass
#
# @bp.route('/user', methods=['POST'])
# def create_user():
#     pass
#
# @bp.route('/user/<int:id>', methods=['PUT'])
# def update_user(id):
#     pass