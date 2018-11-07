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
    operate_type : '1' = 增，改  '2' = 查， '3' = 删, '4' = tryRun, '5' = batch_Run
    '''
    data = request.get_json() or {}
    project_id = data.get('project_id')
    api_id = data.get('api_id')
    env_id = data.get('env_id')
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
    if operate_type == '4':
        if not data:
            return bad_request('no data found to run test')

        name = data.get('name')
        env = Env.query.get_or_404(env_id)

        config = {
            'name': name,
            'request': {
                'base_url': env.env_host,
            },
            'variables': json.loads(env.env_var)  # [{"user_agent": "iOS/10.3"}, {"user_agent": "iOS/10.3"}]
        }
        teststeps = json.loads(data.get('teststeps'))

        payload = []

        for teststep in teststeps:
            if teststep['step_id']:
                step_id = int(teststep['step_id'])
                teststep = TestStep.query.get_or_404(step_id)
            else:
                return bad_request('please add test steps')

            api = Api.query.get_or_404(teststep.api_id)

            if teststep.env_id:
                env = Env.query.get(teststep.env_id)
            else:
                env = None

            data = {
                'name': teststep.name,
                'req_method': api.req_method,
                'req_temp_host': env.env_host if env.env_host else '',
                'req_relate_url': api.req_relate_url,
                'req_data_type': api.req_data_type,
                'req_headers': teststep.req_headers if teststep.req_headers else api.req_headers,   # '{"Content-Type": "application/json"}'
                'req_cookies': teststep.req_cookies if teststep.req_cookies else api.req_cookies,  # '{"token": "application/json"}'
                'req_params': teststep.req_params if teststep.req_params else api.req_params,  # '{"token": "application/json"}'
                'req_body': teststep.req_body if teststep.req_body else api.req_body,   # '{"type": "ios"}'
                'variables': env.env_var if env.env_var else '',  # [{"user_agent": "iOS/10.3"}, ]
                'extracts': env.extracts if env.extracts else '',  # [{"user_agent": "iOS/10.3"}, {"user_agent": "iOS/10.3"}]
                'asserts': env.asserts if env.asserts else ''  # [{'eq': ['status_code', 200]}]
             }
            payload.append(data)
        # print(payload)
        # print(config)
        tester = Runner(payload, config)
        report = tester.run()
        report = json.loads(report)
        return trueReturn(report, 'run success')


@bp.route('/testsBatchRun', methods=['POST'])
def tests_batch_run():
    data = request.get_json() or {}
    project_id = data.get('project_id')
    test_id_items = data.get('test_id_items')

    if len(test_id_items) != 1 or not test_id_items[0]:
        return bad_request('no testcase selected or not support to batch-run currently')

    project = Project.query.get_or_404(project_id)
    if project not in g.current_user.followed_projects().all():
        return bad_request('you are not the member of project %s' % project.project_name)

    for test_id in test_id_items:
        test_id = int(test_id)
        testcase = TestCase.query.get_or_404(test_id)
        if testcase not in project.testcases.all():
            return bad_request('no testcase id %d in project %s' % (test_id, project.project_name))

        name = testcase.name

        env = None
        if testcase.env_id:
            env = Env.query.get_or_404(testcase.env_id)

        config = {
            'name': name,
            'request': {
                'base_url': env.env_host if env else '',
            },
            'variables': json.loads(env.env_var) if env else []  # [{"user_agent": "iOS/10.3"}, {"user_agent": "iOS/10.3"}]
        }
        teststeps = json.loads(testcase.teststeps)

        payload = []

        for teststep in teststeps:
            if teststep['step_id']:
                step_id = int(teststep['step_id'])
                teststep = TestStep.query.get_or_404(step_id)
            else:
                return bad_request('please add test steps')

            api = Api.query.get_or_404(teststep.api_id)

            if teststep.env_id:
                env = Env.query.get(teststep.env_id)
            else:
                env = None

            data = {
                'name': teststep.name,
                'req_method': api.req_method,
                'req_temp_host': env.env_host if env.env_host else '',
                'req_relate_url': api.req_relate_url,
                'req_data_type': api.req_data_type,
                'req_headers': teststep.req_headers if teststep.req_headers else api.req_headers,   # '{"Content-Type": "application/json"}'
                'req_cookies': teststep.req_cookies if teststep.req_cookies else api.req_cookies,  # '{"token": "application/json"}'
                'req_params': teststep.req_params if teststep.req_params else api.req_params,  # '{"token": "application/json"}'
                'req_body': teststep.req_body if teststep.req_body else api.req_body,   # '{"type": "ios"}'
                'variables': env.env_var if env.env_var else '[]',  # [{"user_agent": "iOS/10.3"}, ]
                'extracts': env.extracts if env.extracts else '[]',  # [{"user_agent": "iOS/10.3"}, {"user_agent": "iOS/10.3"}]
                'asserts': env.asserts if env.asserts else '[]'  # [{'eq': ['status_code', 200]}]
             }
            payload.append(data)
        tester = Runner(payload, config)
        result = tester.run()
        result = json.loads(result)

        data = {
            'summary': result,
            'test_result': result['data']['success'],
            'testcase_id': test_id,
            'name': name
        }
        report = Report()
        report.from_dict(data)
        db.session.add(report)
        session_commit()
        response = trueReturn(message='report generated, please check')
        return response
