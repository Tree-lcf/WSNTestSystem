import json
from app.api import bp
from flask import request
from app.models import *
from app.auth.auth import verify_token, token_auth_error
from app.errors import trueReturn, bad_request
from app.common import session_commit, Runner
from app.common import data_to_server


@bp.before_request
def before_request():
    token = request.cookies.get('token')
    if not verify_token(token):
        return token_auth_error()


@bp.route('/apiOperate', methods=['POST'])
def operate_api():
    # operate_type : '1' = 增， '2' = 改， '3' = 查(带API ID)， '4' = 删, '5' = Run, '6' = 筛选查(不带API ID)
    data = request.get_json() or {}
    module_id = data.get('module_id')
    project_id = data.get('project_id')
    api_name = data.get('name')
    api_id = data.get('api_id')
    operate_type = data.get('operate_type')

    if not operate_type:
        return bad_request('must include operate_type')

    # if data.get('req_body'):
    #     req_body = objlist_to_str(data.get('req_body'))
    #     data['req_body'] = req_body
    #
    # if data.get('req_cookies'):
    #     req_cookies = objlist_to_str(data.get('req_cookies'))
    #     data['req_cookies'] = req_cookies

    # 增
    if operate_type == '1':
        if not project_id:
            return bad_request('must include project_id')
        project = Project.query.get_or_404(project_id)
        if project not in g.current_user.followed_projects().all():
            return bad_request('you are not the member of project %s' % project.project_name)
        if not module_id:
            return bad_request('must include module id')
        module = Module.query.get_or_404(module_id)
        if module not in project.modules.all():
            return bad_request('no module %s in project %s' % (module.module_name, project.project_name))

        if not api_name:
            return bad_request('must include api name')
        if Api.query.filter_by(name=api_name).first():
            return bad_request('%s already in project %s' % (api_name, project.project_name))

        api = Api()
        api.from_dict(data)
        db.session.add(api)
        session_commit()

        data = api.to_dict()
        response = trueReturn(data, 'create Api success')
        return response

    # 改
    if operate_type == '2':
        if not api_id:
            return bad_request('must include api_id')
        api = Api.query.get_or_404(api_id)
        if Project.query.get(api.project_id) not in g.current_user.followed_projects().all():
            return bad_request('you are not the member of project')

        if project_id and project_id != api.project_id:
            project = Project.query.get_or_404(project_id)
            if module_id and module_id != api.module_id:
                module = Module.query.get_or_404(module_id)
                if module not in project.modules.all():
                    return bad_request('module %s is not in project %s' % (module.module_name, project.project_name))

        if api_name and api_name != api.name and \
                Api.query.filter_by(name=api_name, project_id=project_id).first():
            return bad_request('please use a different Api name')

        api.from_dict(data)
        db.session.add(api)
        session_commit()

        data = api.to_dict()
        response = trueReturn(data, 'update success')
        return response

    # 查
    if operate_type == '3':
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
        if api_id:
            api = Api.query.get_or_404(api_id)
            if Project.query.get(api.project_id) not in g.current_user.followed_projects().all():
                return bad_request('you are not the member of project')
            return trueReturn(api.to_dict(), 'found it')

        if not project_id and not module_id:
            page_num = int(data.get('page_num', 1))
            per_page = int(data.get('per_page', 10))
            payload = Api.to_collection_dict(page_num, per_page)
            response = trueReturn(payload, 'list success')
            return response

        # if module_id:
        #     module = Module.query.get_or_404(module_id)
        #     project = Project.query.get(module.project_id)
        #     if project not in g.current_user.followed_projects().all():
        #         return bad_request('you are not the member of project')
        #
        #     # api_list = []
        #     # for api in module.apis.all():
        #     #     api_data = api.to_dict()
        #     #     api_list.append(api_data)
        #     # module_data = {
        #     #     'module_id': module.id,
        #     #     'api_list': api_list
        #     # }
        #     response = trueReturn(module_data, 'list module-api success')
        #     return response
        #
        # if project_id:
        #     project = Project.query.get(project_id)
        #     if project not in g.current_user.followed_projects().all():
        #         return bad_request('you are not the member of project')
        #     module_list = []
        #     for module in project.modules.all():
        #         api_list = []
        #         for api in module.apis.all():
        #             api_data = api.to_dict()
        #             api_list.append(api_data)
        #         module_data = {
        #             'module_id': module.id,
        #             'api_list': api_list
        #         }
        #         module_list.append(module_data)
        #     project_data = {
        #         'project_id': project.id,
        #         'module_list': module_list
        #     }
        #     response = trueReturn(project_data, 'list project-module-api success')
        #     return response

    # 删
    if operate_type == '4':
        if not api_id:
            return bad_request('please input api_id')
        for id in api_id:
            api = Api.query.get_or_404(id)
            if Project.query.get(api.project_id) not in g.current_user.followed_projects().all():
                return bad_request('you are not the member of project')
            if api.module_id != module_id or api.project_id != project_id:
                return bad_request('api not in this module or this project, it might be something wrong')
            db.session.delete(api)

        session_commit()
        data = {
            'api_id': api_id
        }
        response = trueReturn(data, 'delete success')
        return response

    # Run
    if operate_type == '5':

        if not data:
            return bad_request('no data found to run test')

        for field in ['req_headers', 'req_cookies', 'req_params', 'req_body']:
            if field in data:
                payload = json.dumps(data_to_server(data.get(field)))
                data[field] = payload

        # print(data)
        tester = Runner([data])
        try:
            # 注意这里没有进行超时返回的处理，后面需要加代码进行处理
            report = tester.run()
        except Exception as e:
            print(e)
            return bad_request('wrong request')

        report = json.loads(report)
        return trueReturn(report, 'run success')

    # 筛选查
    if operate_type == '6':
        if not project_id and not module_id:
            return bad_request('must include project_id or module_id')
        if module_id:
            module = Module.query.get_or_404(module_id)
            project = Project.query.get(module.project_id)
            modules = [module]
        else:
            project = Project.query.get(project_id)
            modules = project.modules.all()

        if project not in g.current_user.followed_projects().all():
            return bad_request('you are not the member of project')

        # project_list = [project]

        # payload = []
        # for project in project_list:
        #     module_list = []
        #     for module in modules:
        #         api_list = []
        #         for api in module.apis.all():
        #             api_data = api.to_dict()
        #             api_list.append(api_data)
        #         module_data = {
        #             'module_id': module.id,
        #             'module_name': module.module_name,
        #             'api_list': api_list
        #         }
        #         module_list.append(module_data)
        #     project_data = {
        #         'project_id': project.id,
        #         'project_name': project.project_name,
        #         'module_list': module_list
        #     }
        #     payload.append(project_data)

        # data = {
        #     'Api_items': payload,
        #     'meta': ''
        # }

        payload = []
        for module in modules:
            payload.append(module.to_dict())

        response = trueReturn(payload, 'special list success')
        return response




