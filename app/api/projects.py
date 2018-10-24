from app.api import bp
from flask import jsonify, request, g
from app.models import *
from app.auth.auth import verify_token, token_auth_error
from app.errors import trueReturn, bad_request
from app.common import session_commit


@bp.before_request
def before_request():
    token = request.cookies.get('token')
    if not verify_token(token):
        return token_auth_error()


@bp.route('/projects', methods=['GET'])
def get_projects():
    page_num = request.args.get('page_num', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    projects_info = Project.to_collection_dict(page_num, per_page)
    response = trueReturn(projects_info, '请求成功')
    return response


@bp.route('/project', methods=['POST'])
def add_project():
    data = request.get_json() or {}
    project_name = data.get('project_name')
    if not project_name:
        return bad_request('must include project name')
    if Project.query.filter_by(project_name=project_name).first():
        return bad_request('please use a different project name')
    project = Project(project_name=project_name)
    db.session.add(project)
    session_commit()
    if project.id:
        data = project.to_dict()
        response = trueReturn(data, '新项目添加成功')
        # response.status_code = 201
        return response
    else:
        return bad_request('新项目添加失败')


@bp.route('/project_has_user', methods=['POST'])
def project_has_user():
    data = request.get_json() or {}
    project_name = data.get('project_name')
    username_list = data.get('username_list')

    if not project_name:
        return bad_request('must include project name')
    project = Project.query.filter_by(project_name=project_name).first()
    if not project:
        return bad_request('项目不存在，请新建')

    for username in username_list:
        # print(username)
        # type(username)
        user = User.query.filter_by(username=username).first()
        if not user:
            return bad_request('用户 %s 不存在' % username)
        project.add_user(user)
        session_commit()

    data = project.to_dict()
    response = trueReturn(data, '该项目添加用户成功')
    # print(data)
    # response.status_code = 201
    return response


@bp.route('/project/<int:id>', methods=['GET'])
def get_project(id):
    return jsonify(Project.query.get_or_404(id).to_dict())
#
# def get_project(id):
#     project = Project
#     user = User.query.get_or_404(id)
#     page = request.args.get('page', 1, type=int)
#     per_page = min(request.args.get('per_page', 10, type=int), 100)
#     data = User.to_collection_dict(user.followers, page, per_page,
#                                    'api.get_followers', id=id)
#     return jsonify(data)
#     # print(g.current_user.projects.all())
#     # print(projects.items)
#     data = {
#         'projects_info': [project.to_dict() for project in projects.items],
#         'has_next': projects.has_next,
#         'next_num': projects.next_num,
#         'has_prev': projects.has_prev,
#         'prev_num': projects.prev_num
#     }
#
#     response = trueReturn(data, '请求成功')
#     return response


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