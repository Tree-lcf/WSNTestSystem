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
    project_id = data.get('project_id')
    env_name = data.get('env_name')
    env_id = data.get('env_id')
    operate_type = data.get('operate_type')

    if not operate_type:
        return bad_request('must include operate_type')

    # 增
    if operate_type == '1':
        if not project_id:
            return bad_request('must include project_id')
        project = Project.query.get_or_404(project_id)
        if project not in g.current_user.followed_projects().all():
            return bad_request('you are not the member of project %s' % project.project_name)

        if not env_name:
            return bad_request('must include environment name')
        if Env.query.filter_by(env_name=env_name).first():
            return bad_request('there is environment %s in this project %s' % (env_name, project.project_name))

        env = Env()
        env.from_dict(data)
        db.session.add(env)
        session_commit()

        data = env.to_dict()
        response = trueReturn(data, 'create environment success')
        return response

    # 改
    if operate_type == '2':
        if project_id:
            project = Project.query.get_or_404(project_id)
            if project not in g.current_user.followed_projects().all():
                return bad_request('you are not the member of project %s' % project.project_name)

        env = Env.query.get_or_404(env_id)
        if Project.query.get(env.project_id) not in g.current_user.followed_projects().all():
            return bad_request('you are not the member of project')

        if env_name and env_name != env.env_name and \
                Env.query.filter_by(env_name=env_name).first():
            return bad_request('please use a different environment name or version')
        # if env_version and env_version != env.env_version and \
        #         Env.query.filter_by(env_name=env_name, env_version=env_version).first():
        #     return bad_request('please use a different environment name or version')

        env.from_dict(data)
        db.session.add(env)
        session_commit()

        data = env.to_dict()
        response = trueReturn(data, 'update environment success')
        return response

    # 查
    if operate_type == '3':
        '''
        [{
        'project_name': project_name,
        'env_list':[{}]
        }]
        '''
        if env_id:
            env = Env.query.get_or_404(env_id)
            return trueReturn(env.to_dict(), 'found it')

        page_num = int(data.get('page_num', 1))
        per_page = int(data.get('per_page', 10))
        payload = Env.to_collection_dict(page_num, per_page)
        response = trueReturn(payload, 'list success')
        return response

    # 删
    if operate_type == '4':
        if not env_id:
            return bad_request('please input env_id')
        env = Env.query.get_or_404(env_id)

        if Project.query.get(env.project_id) not in g.current_user.followed_projects().all():
            return bad_request('you are not the member of project')

        if env.testcases.all() or env.teststeps.all():
            return bad_request('there are tests under this env, please delete those tests first')

        db.session.delete(env)
        session_commit()
        data = {
            'env_id': env_id
        }
        response = trueReturn(data, 'delete success')
        return response
