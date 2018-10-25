from app.api import bp
from flask import request, g
from app.models import *
from app.auth.auth import verify_token, token_auth_error
from app.errors import trueReturn, bad_request, error_response
from app.common import session_commit


@bp.before_request
def before_request():
    token = request.cookies.get('token')
    if not verify_token(token):
        return token_auth_error()


@bp.route('/projectsList', methods=['GET'])
def get_projects():
    page_num = request.args.get('page_num', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    projects_info = Project.to_collection_dict(page_num, per_page)
    response = trueReturn(projects_info, '请求成功')
    return response


@bp.route('/projectCreate', methods=['POST'])
def create_project():
    data = request.get_json() or {}
    project_name = data.get('project_name')
    owner_name = data.get('owner_name')
    if not project_name or not owner_name:
        return bad_request('must include project name or owner_name')

    if Project.query.filter_by(project_name=project_name).first():
        return bad_request('please use a different project name')

    if not User.query.filter_by(username=owner_name).first():
        return bad_request('owner does not exist')

    project = Project(project_name=project_name, owner_name=owner_name)
    db.session.add(project)
    session_commit()
    project = Project.query.filter_by(project_name=project_name).first()
    if not project:
        return bad_request('create project fail')
    # project.add_user(g.current_user)
    # admins = User.admins_list()
    # if admins:
    #     for admin in admins:
    #         project.add_user(admin)
    # session_commit()
    data = project.to_dict()
    response = trueReturn(data, 'create project successfully')
    # response.status_code = 201
    return response


@bp.route('/projectUpdate', methods=['POST'])
def update_project():
    data = request.get_json() or {}
    origin_project_name = data.get('origin_project_name')
    origin_owner_name = data.get('origin_owner_name')
    new_owner_name = data.get('owner_name')
    new_project_name = data.get('project_name')

    origin_user = User.query.filter_by(username=origin_owner_name).first()
    if not origin_user:
        return bad_request('owner does not exist')
    origin_project = Project.query.filter_by(project_name=origin_project_name).first()
    if not origin_project:
        return bad_request('original project %s does not exist' % origin_project_name)

    # print(g.current_user)
    # print(origin_user)
    if origin_user != g.current_user:
        return bad_request('you are not the owner of %s project, cannot update it' % origin_project_name)

    if new_owner_name and new_owner_name != origin_owner_name and \
            not User.query.filter_by(username=new_owner_name).first():
        return bad_request('please use a registered username')
    if new_project_name and new_project_name != origin_project_name and \
            Project.query.filter_by(project_name=new_project_name).first():
        return bad_request('please use a different project name')

    origin_project.from_dict(data)
    db.session.add(origin_project)
    session_commit()

    project = Project.query.filter_by(project_name=new_project_name).first()
    if not project:
        return bad_request('update project fail')

    data = project.to_dict()
    response = trueReturn(data, 'update project successfully')
    return response


@bp.route('/projectInfo', methods=['GET'])
def get_project_info():
    project_name = request.args.get('project_name', type=str)
    if not project_name:
        return bad_request('must include project name')

    project = g.current_user.followed_projects().filter_by(project_name=project_name).first()

    if not project:
        return bad_request('%s is not the member of %s' % (g.current_user.username, project_name))

    data = project.to_dict()
    response = trueReturn(data, 'Success')
    return response


@bp.route('/projectDel', methods=['POST'])
def delete_project():
    data = request.get_json() or {}
    project_name = data.get('project_name')
    if not project_name:
        return bad_request('must include project name')

    # project = g.current_user.projects.filter_by(project_name=project_name).first()
    project = Project.query.filter_by(project_name=project_name).first()

    if not project:
        return bad_request('%s project does not exist' % project_name)

    if project.owner_name != g.current_user.username:
        return bad_request('you are not owner of %s project, cannot delete it' % project_name)

    if project.users.first():
        return bad_request('Cannot delete it as there are users in %s' % project_name)

    if project.modules.first():
        return bad_request('Cannot delete it as there are modules in %s' % project_name)

    if project.envs.first():
        return bad_request('Cannot delete it as there are envs in %s' % project_name)

    if project.scenes.first():
        return bad_request('Cannot delete it as there are scenes in %s' % project_name)

    db.session.delete(project)
    session_commit()

    if not Project.query.filter_by(project_name=project_name).first():
        response = trueReturn(message='delete project successfully')
        # response.status_code = 201
        return response
    else:
        return bad_request('delete project fail')


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
        if user in project.users.all():
            return bad_request('用户 %s 已添加' % username)
        if user.username == project.owner_name:
            return bad_request('用户 %s 是该项目Owner，无需添加' % username)
        project.follow(user)
        session_commit()

    data = project.to_dict()
    response = trueReturn(data, '该项目添加用户成功')
    # print(data)
    # response.status_code = 201
    return response



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