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


@bp.route('/moduleOperate', methods=['POST'])
def operate_module():
    data = request.get_json() or {}
    project_name = data.get('project_name')
    module_name = data.get('module_name')
    origin_name = data.get('origin_name')
    operate_type = data.get('operate_type')

    if not project_name:
        return bad_request('must include project name')
    if not operate_type:
        return bad_request('must include operate_type')
    project = Project.query.filter_by(project_name=project_name).first_or_404()
    if project.owner_name != g.current_user.username:
        return bad_request('you are not the owner of project %s' % project_name)

    # 增
    if operate_type == '1':
        if not module_name:
            return bad_request('please input module name')
        module = Module.query.filter_by(module_name=module_name).first()
        if module:
            return bad_request('there is module %s in this project %s' % (module_name, project_name))

        data = {
            'module_name': module_name,
            'project_id': project.id
        }
        module = Module()
        module.from_dict(data)
        db.session.add(module)
        session_commit()

        data = module.to_dict()
        response = trueReturn(data, 'create module success')
        return response

    # 改
    if operate_type == '2':
        module = Module.query.filter_by(module_name=origin_name).first_or_404()

        if not module_name or module_name == '':
            return bad_request('please input a new module name')

        if module_name == origin_name:
            return bad_request('no change')

        if Module.query.filter_by(module_name=module_name).first():
            return bad_request('please use a different module name')

        module.module_name = module_name
        db.session.add(module)
        session_commit()

        data = module.to_dict()
        response = trueReturn(data, 'update module success')
        return response

    # 查
    if operate_type == '3':
        data = project.to_dict()['modules']
        response = trueReturn(data, 'list success')
        return response

    # 删
    if operate_type == '4':
        if not origin_name:
            return bad_request('please input module name')
        module = Module.query.filter_by(module_name=origin_name).first_or_404()
        db.session.delete(module)
        session_commit()

        response = trueReturn(data, 'delete success')
        return response


@bp.route('/moduleList', methods=['POST'])
def get_modules():
    data = request.get_json() or {}
    project_name = data.get('project_name')
    if not project_name:
        return bad_request('must include project name')
    project = Project.query.filter_by(project_name=project_name).first_or_404()
    if project.owner_name != g.current_user.username:
        return bad_request('you are not the owner of project %s' % project_name)

    data = project.to_dict()['modules']
    response = trueReturn(data, 'success')
    return response


@bp.route('/moduleCreate', methods=['POST'])
def create_module():
    data = request.get_json() or {}
    project_name = data.get('project_name')
    module_name = data.get('module_name')
    if not project_name:
        return bad_request('must include project name')
    project = Project.query.filter_by(project_name=project_name).first_or_404()

    if project.owner_name != g.current_user.username:
        return bad_request('you are not the owner of project %s' % project_name)

    module = Module.query.filter_by(module_name=module_name).first()
    if module:
        return bad_request('there is module %s in this project %s' % (module_name, project_name))

    data = {
        'module_name': module_name,
        'project_id': project.id
    }
    module = Module()
    module.from_dict(data)
    db.session.add(module)
    session_commit()
    data = project.to_dict()['modules']
    response = trueReturn(data, 'success')
    return response


@bp.route('/modulesDel', methods=['POST'])
def delete_module():
    data = request.get_json() or {}
    project_name = data.get('project_name')
    module_name = data.get('module_name')
    if not project_name:
        return bad_request('must include project name')
    project = Project.query.filter_by(project_name=project_name).first_or_404()
    if project.owner_name != g.current_user.username:
        return bad_request('you are not the owner of project %s' % project_name)

    module = Module.query.filter_by(module_name=module_name).first_or_404()
    db.session.delete(module)
    session_commit()
    data = project.to_dict()['modules']
    response = trueReturn(data, 'success')
    return response


@bp.route('/modulesUpdate', methods=['POST'])
def update_module():
    data = request.get_json() or {}
    project_name = data.get('project_name')
    update_info_list = data.get('update_info_list')
    '''
    update_info_list: [{'origin_name1':'','new_name1':''},{'origin_name2':'','new_name2':''}]    
    '''
    if not project_name:
        return bad_request('must include project name')
    project = Project.query.filter_by(project_name=project_name).first_or_404()
    if project.owner_name != g.current_user.username:
        return bad_request('you are not the owner of project %s' % project_name)

    if not update_info_list:
        data = project.to_dict()['modules']
        response = trueReturn(data, 'success')
        return response

    new_name_list = []
    for module_info in update_info_list:
        origin_name = module_info['origin_name']
        new_name = module_info['new_name']
        module = Module.query.filter_by(module_name=origin_name).first_or_404()

        if not new_name or new_name == '':
            return bad_request('please input a new module name')

        if new_name == origin_name:
            continue

        if Module.query.filter_by(module_name=new_name).first() or new_name in new_name_list:
            return bad_request('please use a different module name')

        module.module_name = new_name
        db.session.add(module)
        new_name_list.append(new_name)

    session_commit()
    data = project.to_dict()['modules']
    response = trueReturn(data, 'success')
    return response


# @bp.route('/modules', methods=['POST'])
# def operate_modules():
#     data = request.get_json() or {}
#     project_name = data.get('project_name')
#     oper_type = data.get('oper_type')  # query = 1, update = 2
#
#     if not oper_type or oper_type not in ['1', '2']:
#         return bad_request('oper_type error')
#
#     if not project_name:
#         return bad_request('must include project name')
#
#     project = Project.query.filter_by(project_name=project_name).first_or_404()
#
#     if project.owner_name != g.current_user:
#         return bad_request('you are not the owner of project %s' % project_name)
#
#     if oper_type == '1':
#         data = project.to_dict()
#         response = trueReturn(data, 'success')
#         return response
#
#     else:
#         module_name_list = set(data.get('module_name_list'))
#         for module_name in module_name_list:
#             module = Module.query.filter_by(module_name=module_name).first()
#             if module in project.modules.all():
#                 return bad_request('there is %s already in project %s' % (module_name, project_name))
#             data = {
#                 'module_name': module_name,
#                 'project_id': project.id
#             }
#             module = Module()
#             module.from_dict(data)
#             db.session.add(module)
#             session_commit()
#
#             if oper_type == '2':
#                 if module not in project.modules.all():
#                     return bad_request('there is not module %s in project %s' % (module_name, project_name))
#                 db.session.delete(module)
#
#     data = project.to_dict()
#
#     if follow_type == '1':
#         response = trueReturn(data, 'add users into project %s success' % project_name)
#         return response
#
#     if follow_type == '2':
#         response = trueReturn(data, 'remove users from project %s success' % project_name)
#         return response


