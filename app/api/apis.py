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


@bp.route('/apiOperate', methods=['POST'])
def operate_api():
    '''
    api_id
    api_name
    req_method
    req_temp_host
    req_relat_url
    req_headers
    req_params
    req_data_type
    req_body
    timestamp
    module_id
    project_id
    operate_type : '1' = 增， '2' = 改， '3' = 查， '4' = 删, '5' = Run
    '''
    data = request.get_json() or {}
    module_id = data.get('module_id')
    project_id = data.get('project_id')
    api_name = data.get('api_name')
    # env_version = data.get('env_version')
    api_id = data.get('api_id')
    operate_type = data.get('operate_type')

    if not operate_type:
        return bad_request('must include operate_type')

    # 增
    if operate_type == '1':
        if not module_id:
            return bad_request('must include module id')

        module = Module.query.get_or_404(module_id)
        project = Project.query.get_or_404(project_id)

        if project not in g.current_user.followed_projects().all():
            return bad_request('you are not the member of project %s' % project.project_name)

        if module not in project.modules.all():
            return bad_request('no module %s in project %s' % (module.module_name, project.project_name))

        if not api_name:
            return bad_request('must include api name')
        if Api.query.filter_by(api_name=api_name).first():
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
        if project_id:
            project = Project.query.get_or_404(project_id)
            if project not in g.current_user.followed_projects().all():
                return bad_request('you are not the member of project %s' % project.project_name)

        if module_id:
            module = Module.query.get_or_404(module_id)
            if module not in project.modules.all():
                return bad_request('module %s is not in project %s' % (module.module_name, project.project_name))

        api = Api.query.get_or_404(api_id)
        if Project.query.get(api.project_id) not in g.current_user.followed_projects().all():
            return bad_request('you are not the member of project')

        if api_name and api_name != api.api_name and \
                Api.query.filter_by(api_name=api_name, project_id=project_id).first():
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
        page_num = int(data.get('page_num', 1))
        per_page = int(data.get('per_page', 10))
        payload = Api.to_collection_dict(page_num, per_page)
        response = trueReturn(payload, 'list success')
        return response

    # 删
    if operate_type == '4':
        if not api_id:
            return bad_request('please input api_id')
        api = Api.query.get_or_404(api_id)

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
