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


@bp.route('/report', methods=['POST'])
def operate_report():
    '''
    operate_type : '1' = 增，改  '2' = 查
    '''
    data = request.get_json() or {}
    report_id = data.get('report_id')

    if not report_id:
        return bad_request('please select a report to view')
    report = Report.query.get_or_404(int(report_id))
    testcase = TestCase.query.get_or_404(report.testcase_id)
    project = Project.query.get_or_404(testcase.project_id)

    if project not in g.current_user.followed_projects().all():
        return bad_request('you are not the member of project %s' % project.project_name)

    # 查
    data = report.to_dict()
    return trueReturn(data, 'found it')
