import json
from app.api import bp
from flask import request, g
from app.models import *
from app.auth.auth import verify_token, token_auth_error
from app.errors import trueReturn, bad_request
from app.common import session_commit
from app.utils.http_run import Runner


@bp.before_request
def before_request():
    token = request.cookies.get('token')
    if not verify_token(token):
        return token_auth_error()


@bp.route('/testCaseOperate', methods=['POST'])
def operate_testcase():
    '''
    operate_type : '1' = 增，改  '2' = 查， '3' = 删, '4' = Run
    '''
    data = request.get_json() or {}
    project_id = data.get('project_id')
    api_id = data.get('api_id')
    testcase_id = data.get('testcase_id')
    testcase_name = data.get('name')
    operate_type = data.get('operate_type')

    if not operate_type:
        return bad_request('must include operate_type')

    # 增，改
    if operate_type == '1':

        project = Project.query.get_or_404(project_id)
        api = Api.query.get_or_404(api_id)

        if project not in g.current_user.followed_projects().all():
            return bad_request('you are not the member of project %s' % project.project_name)

        if api not in project.apis.all():
            return bad_request('no api %s in project %s' % (api.name, project.project_name))

        if not testcase_id:
            if not testcase_name:
                return bad_request('please input testcase name')
            if TestCase.query.filter_by(name=testcase_name).first():
                return bad_request('Testcase %s already exists' % testcase_name)

            testcase = TestCase()
            testcase.from_dict(data)
            db.session.add(testcase)
            session_commit()
            data = testcase.to_dict()
            response = trueReturn(data, 'create testcase success')
            return response

        if testcase_id:
            testcase = TestCase.query.get_or_404(testcase_id)
            if Project.query.get(testcase.project_id) not in g.current_user.followed_projects().all():
                return bad_request('you are not the member of project')

            if testcase_name and testcase_name != testcase.name \
                    and TestCase.query.filter_by(name=testcase_name).first():
                return bad_request('please use a different testcase name')

            testcase.from_dict(data)
            db.session.add(testcase)
            session_commit()

            data = testcase.to_dict()
            response = trueReturn(data, 'update testcase success')
            return response

    # 查
    if operate_type == '2':
        if testcase_id:
            testcase = TestCase.query.get_or_404(testcase_id)
            return trueReturn(testcase.to_dict(), 'found it')

        page_num = int(data.get('page_num'))
        per_page = int(data.get('per_page'))
        payload = TestCase.to_collection_dict(page_num, per_page)
        response = trueReturn(payload, 'list success')
        return response

    # 删
    if operate_type == '3':
        if not testcase_id:
            return bad_request('please input testcase_id')
        for id in testcase_id:
            testcase = TestCase.query.get_or_404(id)
            if Project.query.get(testcase.project_id) not in g.current_user.followed_projects().all():
                return bad_request('cannot delete it as you are not the member of project')
            db.session.delete(testcase)

        session_commit()
        data = {
            'testcase_id': testcase_id
        }
        response = trueReturn(data, 'delete success')
        return response

    # Run
    if operate_type == '5':
        if not data:
            return bad_request('no data found to run test')

        tester = Runner([data])
        report = tester.run()
        report = json.loads(report)
        return trueReturn(report, 'run success')

