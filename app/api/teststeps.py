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


@bp.route('/testStepOperate', methods=['POST'])
def operate_teststep():
    '''
    operate_type : '1' = 增，改  '2' = 查， '3' = 删
    '''
    data = request.get_json() or {}
    api_id = data.get('api_id')
    teststep_name = data.get('name')
    teststep_id = data.get('teststep_id')
    operate_type = data.get('operate_type')

    if not operate_type:
        return bad_request('must include operate_type')

    api = Api.query.get_or_404(api_id)
    project = Project.query.get_or_404(api.project_id)

    if project not in g.current_user.followed_projects().all():
        return bad_request('you are not the member of project %s' % project.project_name)

    # 增，改
    if operate_type == '1':
        if not teststep_id:
            if not teststep_name:
                return bad_request('please input teststep_name')
            if TestStep.query.filter_by(name=teststep_name, api_id=api_id).first():
                return bad_request('Teststep %s already exists' % teststep_name)

            teststep = TestStep()
            teststep.from_dict(data)
            db.session.add(teststep)
            session_commit()

            data = teststep.to_dict()
            response = trueReturn(data, 'create teststep success')
            return response

        if teststep_id:
            teststep = TestStep.query.get_or_404(teststep_id)

            if teststep_name and teststep_name != teststep.name \
                    and TestStep.query.filter_by(name=teststep_name).first():
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
            return trueReturn(teststep.to_dict(), 'found it')
        else:
            return bad_request('please select one teststep')

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

