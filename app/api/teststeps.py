from app.api import bp
from flask import request
from app.models import *
from app.auth.auth import verify_token, token_auth_error
from app.errors import trueReturn, bad_request
from app.common import session_commit, Runner


@bp.before_request
def before_request():
    token = request.cookies.get('token')
    if not verify_token(token):
        return token_auth_error()


@bp.route('/testStepOperate', methods=['POST'])
def operate_teststep():
    '''
    operate_type : '1' = 增，改  '2' = 查， '3' = 删，'4' = 运行
    '''
    data = request.get_json() or {}
    api_id = data.get('api_id')
    name = data.get('name')
    teststep_id = data.get('teststep_id')
    operate_type = data.get('operate_type')
    project_id = data.get('project_id')
    module_id = data.get('module_id')

    if not operate_type:
        return bad_request('must include operate_type')

    # api = Api.query.get_or_404(api_id)
    project = Project.query.get_or_404(project_id)

    if project not in g.current_user.followed_projects().all():
        return bad_request('you are not the member of project %s' % project.project_name)

    # 增，改
    if operate_type == '1':
        if not teststep_id:
            if not name:
                return bad_request('please input teststep_name')
            if TestStep.query.filter_by(name=name, api_id=api_id).first():
                return bad_request('Teststep %s already exists' % name)

            teststep = TestStep()
            teststep.from_dict(data)
            db.session.add(teststep)
            session_commit()

            data = teststep.to_dict()
            response = trueReturn(data, 'create teststep success')
            return response

        if teststep_id:
            teststep = TestStep.query.get_or_404(teststep_id)

            if name and name != teststep.name \
                    and TestStep.query.filter_by(name=name).first():
                return bad_request('please use a different teststep name')

            teststep.from_dict(data)
            db.session.add(teststep)
            session_commit()

            data = teststep.to_dict()
            response = trueReturn(data, 'update teststep success')
            return response

    # 查
    if operate_type == '2':
        if teststep_id:
            teststep = TestStep.query.get_or_404(teststep_id)
            api = Api.query.get_or_404(teststep.api_id)
            if Project.query.get_or_404(api.project_id) not in g.current_user.followed_projects().all():
                return bad_request('you are not the member of project')
            return trueReturn(teststep.to_dict(), 'found it')

        if api_id:
            api = Api.query.get_or_404(api_id)
            project = Project.query.get(api.project_id)
            if project not in g.current_user.followed_projects().all():
                return bad_request('you are not the member of project')
            response = trueReturn(api.to_collection_step_dict(), 'list api-steps success')
            return response

        if module_id:
            module = Module.query.get_or_404(module_id)
            project = Project.query.get(module.project_id)
            if project not in g.current_user.followed_projects().all():
                return bad_request('you are not the member of project')
            response = trueReturn(module.to_collection_step_dict(), 'list module-steps success')
            return response

        if project_id:
            project = Project.query.get(project_id)
            if project not in g.current_user.followed_projects().all():
                return bad_request('you are not the member of project')
            response = trueReturn(project.to_collection_step_dict(), 'list project-steps success')
            return response
        else:
            return bad_request('please input info for querying')

    # 删
    if operate_type == '3':
        if not teststep_id:
            return bad_request('please select one teststep at least')

        teststep = TestStep.query.get_or_404(teststep_id)

        db.session.delete(teststep)

        session_commit()
        data = {
            'teststep_id': teststep_id
        }
        response = trueReturn(data, 'delete success')
        return response

    # Run
    if operate_type == '4':
        teststep = TestStep.query.get_or_404(teststep_id)
        env = Env.query.get_or_404(teststep.env_id)
        config = {
            'name': teststep.name,
            'request': {
                'base_url': env.env_host,
            },
            'variables': json.loads(env.env_var)  # [{"user_agent": "iOS/10.3"}, {"user_agent": "iOS/10.3"}]
        }

        api = Api.query.get_or_404(teststep.api_id)

        data = {
            'name': teststep.name,
            'req_method': api.req_method,
            'req_temp_host': env.env_host if env.env_host else '',
            'req_relate_url': api.req_relate_url,
            'req_data_type': api.req_data_type,
            'req_headers': teststep.req_headers if teststep.req_headers else api.req_headers,
        # '{"Content-Type": "application/json"}'
            'req_cookies': teststep.req_cookies if teststep.req_cookies else api.req_cookies,
        # '{"token": "application/json"}'
            'req_params': teststep.req_params if teststep.req_params else api.req_params,
        # '{"token": "application/json"}'
            'req_body': teststep.req_body if teststep.req_body else api.req_body,  # '{"type": "ios"}'
            'variables': env.env_var if env.env_var else '',  # [{"user_agent": "iOS/10.3"}, ]
            'extracts': env.extracts if env.extracts else '',
        # [{"user_agent": "iOS/10.3"}, {"user_agent": "iOS/10.3"}]
            'asserts': env.asserts if env.asserts else ''  # [{'eq': ['status_code', 200]}]
        }
        # print(data)
        # print(config)
        tester = Runner([data], config)
        summary = tester.run()
        summary = json.loads(summary)
        # return trueReturn(report, 'run success')

        print(summary)
        # 这里summary格式为dict，理论应该为string，需要明天试一下，testcase那里也有同样问题

        data = {
            'summary': summary,
            'test_result': summary['details'][0]['records'][0]['meta_data']['response']['ok'],
            'teststep_id': teststep.id,
            'name': teststep.name
        }

        # 这段代码是为了之后，若只保留一个测试报告，对原有报告进行更新的时候使用
        report_o = teststep.reports.order_by(Report.timestamp.desc()).first()
        if not report_o:
            report = Report()
        else:
            report = report_o

        # report = Report()
        report.from_dict(data)
        db.session.add(report)
        session_commit()

        response = trueReturn({'report_id': report.id}, 'test run complete')
        return response
