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


@bp.route('/suiteOperate', methods=['POST'])
def operate_env():
    '''
    :input:
    {
        'project_id': project_id,
        'suite_name': suite_name,
        'suite_id': suite_id,
        'operate_type': operate_type
    }
    '''

    data = request.get_json() or {}
    project_id = data.get('project_id')
    suite_name = data.get('suite_name')
    suite_id = data.get('suite_id')
    operate_type = data.get('operate_type')

    if not operate_type:
        return bad_request('must include operate_type')
    if not project_id:
        return bad_request('must include project_id')
    project = Project.query.get_or_404(project_id)
    if project not in g.current_user.followed_projects().all():
        return bad_request('you are not the member of project %s' % project.project_name)

    # 增
    if operate_type == '1':
        if not suite_name:
            return bad_request('must include suite name')
        if Suite.query.filter_by(suite_name=suite_name).first():
            return bad_request('there is test suite %s in this project %s' % (suite_name, project.project_name))

        suite = Suite()
        suite.from_dict(data)
        db.session.add(suite)
        session_commit()

        data = suite.to_dict()
        response = trueReturn(data, 'create suite success')
        return response

    # 改
    if operate_type == '2':
        suite = Env.query.get_or_404(suite_id)
        if Project.query.get(suite.project_id) not in g.current_user.followed_projects().all():
            return bad_request('you are not the member of project')

        if suite_name and suite_name != suite.suite_name and \
                Suite.query.filter_by(suite_name=suite_name).first():
            return bad_request('please use a different test suite name')

        suite.from_dict(data)
        db.session.add(suite)
        session_commit()

        data = suite.to_dict()
        response = trueReturn(data, 'update test suite success')
        return response

    # 查
    if operate_type == '3':
        '''
        [{
        'project_name': project_name,
        'env_list':[{}]
        }]
        '''

        response = trueReturn(project.to_collection_suite_dict(), 'list project-suites success')
        return response

    # 删
    if operate_type == '4':
        if not suite_id:
            return bad_request('please input suite_id')
        suite = Suite.query.get_or_404(suite_id)

        if Project.query.get(suite.project_id) not in g.current_user.followed_projects().all():
            return bad_request('you are not the member of project')

        if suite.testcases.all():
            return bad_request('there are tests under this test suite, please delete those tests first')

        db.session.delete(suite)
        session_commit()
        data = {
            'suite_id': suite_id
        }
        response = trueReturn(data, 'delete success')
        return response
