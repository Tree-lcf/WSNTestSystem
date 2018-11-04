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


@bp.route('/testOperate', methods=['POST'])
def operate_test():
    '''
    operate_type : '1' = 增，改  '2' = 查， '3' = 删, '4' = Run
    '''
    data = request.get_json() or {}
    project_id = data.get('project_id')
    api_id = data.get('api_id')
    test_id = data.get('test_id')
    test_name = data.get('name')
    test_ver = data.get('test_ver')
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

        if not test_id:
            if not (test_name or test_ver):
                return bad_request('please input test name or version')
            if Test.query.filter_by(name=test_name, test_ver=test_ver).first():
                return bad_request('Test %s already exists' % test_name)

            test = Test()
            test.from_dict(data)
            db.session.add(test)
            session_commit()
            data = test.to_dict()
            response = trueReturn(data, 'create test success')
            return response

        if test_id:
            test = Test.query.get_or_404(test_id)
            if Project.query.get(test.project_id) not in g.current_user.followed_projects().all():
                return bad_request('you are not the member of project')

            if (test_name or test_ver) and (test_name != test.name or test_ver != test.test_ver)\
                    and Test.query.filter_by(name=test_name, test_ver=test_ver).first():
                return bad_request('please use a different test name or version')

            test.from_dict(data)
            db.session.add(test)
            session_commit()

            data = test.to_dict()
            response = trueReturn(data, 'update test success')
            return response

    # 查
    if operate_type == '2':
        '''
           [{
           'project_id': project_id,
           'module_list':[
               {
                   'module_id': module_id,
                   'api_list': [{}]        
                }
           ]
           }]
        '''

        if test_id:
            test = Test.query.get_or_404(test_id)
            return trueReturn(test.to_dict(), 'found it')

        page_num = int(data.get('page_num'))
        per_page = int(data.get('per_page'))
        payload = Test.to_collection_dict(page_num, per_page)
        response = trueReturn(payload, 'list success')
        return response

    # 删
    if operate_type == '3':
        if not test_id:
            return bad_request('please input test_id')
        for id in test_id:
            test = Test.query.get_or_404(id)
            if Project.query.get(test.project_id) not in g.current_user.followed_projects().all():
                return bad_request('cannot delete it as you are not the member of project')
            db.session.delete(test)

        session_commit()
        data = {
            'test_id': test_id
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

