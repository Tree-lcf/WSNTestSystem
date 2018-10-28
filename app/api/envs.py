from app.api import bp
from flask import request, g
from app.models import *
from app.auth.auth import verify_token, token_auth_error
from app.errors import trueReturn, bad_request
from app.common import session_commit


@bp.before_request
def before_request():
    token = request.cookies.get('token')
    if not verify_token(token):
        return token_auth_error()


@bp.route('/envOperate', methods=['POST'])
def operate_env():
    data = request.get_json() or {}
    project_name = data.get('project_name')
    env_name = data.get('env_name')
    env_version = data.get('env_version')
    origin_name = data.get('origin_name')
    origin_version = data.get('origin_version')
    operate_type = data.get('operate_type')

    if not project_name or not operate_type:
        return bad_request('must include project name or operate_type')

    project = Project.query.filter_by(project_name=project_name).first_or_404()
    if project.owner_name != g.current_user.username:
        return bad_request('you are not the owner of project %s' % project_name)

    # 增
    if operate_type == '1':
        if not env_name or not env_version:
            return bad_request('must include environment name or operate_type')
        env = Env.query.filter_by(env_name=env_name).first()
        if env:
            return bad_request('there is environment %s in this project %s' % (env_name, project_name))

        # data = {
        #     'module_name': module_name,
        #     'project_id': project.id
        # }
        env = Env()
        env.from_dict(data)
        db.session.add(env)
        session_commit()

        data = env.to_dict()
        response = trueReturn(data, 'create environment success')
        return response

    # 改
    if operate_type == '2':
        env = Env.query.filter_by(env_name=origin_name).first_or_404()

        if 'env_name' and env_name != origin_name and \
                Env.query.filter_by(env_name=env_name).first():
            return bad_request('please use a different environment name')
        if 'env_version' and env_version != origin_version and \
                Env.query.filter_by(env_version=env_version).first():
            return bad_request('please use a different environment version')

        env.from_dict(data)
        db.session.add(env)
        session_commit()

        data = env.to_dict()
        response = trueReturn(data, 'update environment success')
        return response

    # 查
    if operate_type == '3':
        data = {
            'project_name': project_name,
            'modules': project.to_dict()['modules']
        }
        response = trueReturn(data, 'list success')
        return response

    # 删
    if operate_type == '4':
        if not origin_name:
            return bad_request('please input environment name')
        env = Env.query.filter_by(env_name=origin_name).first_or_404()
        db.session.delete(env)
        session_commit()
        data = origin_name
        response = trueReturn(data, 'delete success')
        return response
