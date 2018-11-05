import json
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


@bp.route('/testConfOperate', methods=['POST'])
def operate_testconf():
    '''
    operate_type : '1' = 增，改  '2' = 查， '3' = 删
    '''
    data = request.get_json() or {}
    api_id = data.get('api_id')
    testconf_id = data.get('testconf_id')
    operate_type = data.get('operate_type')

    if not operate_type:
        return bad_request('must include operate_type')

    api = Api.query.get_or_404(api_id)
    project = Project.query.get_or_404(api.project_id)

    if project not in g.current_user.followed_projects().all():
        return bad_request('you are not the member of project %s' % project.project_name)

    # 增，改
    if operate_type == '1':
        if not testconf_id:
            testconf = TestConf()
            testconf.from_dict(data)
            db.session.add(testconf)
            session_commit()
            data = testconf.to_dict()
            response = trueReturn(data, 'create testconf success')
            return response

        if testconf_id:
            testconf = TestConf.query.get_or_404(testconf_id)
            testconf.from_dict(data)
            db.session.add(testconf)
            session_commit()

            data = testconf.to_dict()
            response = trueReturn(data, 'update testconf success')
            return response

    # 查
    if operate_type == '2':
        if testconf_id:
            testconf = TestConf.query.get_or_404(testconf_id)
            return trueReturn(testconf.to_dict(), 'found it')
        else:
            return bad_request('must include testconf_id')

    # 删
    if operate_type == '3':
        if not testconf_id:
            return bad_request('must include testconf_id')

        testconf = TestConf.query.get_or_404(testconf_id)

        db.session.delete(testconf)

        session_commit()
        data = {
            'testconf_id': testconf_id
        }
        response = trueReturn(data, 'delete success')
        return response

