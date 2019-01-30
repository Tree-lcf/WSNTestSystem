from app.api import bp
from flask import request
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
    operate_type : '1' = 根据step只查一个最新报告, '2' = 查, '3' = 删
    '''
    data = request.get_json() or {}
    report_id = data.get('report_id')
    operate_type = data.get('operate_type')
    teststep_id = data.get('teststep_id')

    if not operate_type:
        return bad_request('must include operate_type')

    # '1' = 查
    if operate_type == '1':
        if not teststep_id or not testcase_id:
            return bad_request('must include teststep_id or testcase_id')

        if teststep_id:
            teststep = TestStep.query.get_or_404(int(teststep_id))
            project = Project.query.get_or_404(teststep.project_id)

            if project not in g.current_user.followed_projects().all():
                return bad_request('you are not the member of project')
            report = teststep.reports.order_by(Report.timestamp.desc()).first()
            data = report.to_dict()
            return trueReturn(data, 'found it')

        if report_id:
            report = Report.query.get_or_404(int(report_id))
            testcase_id = report.testcase_id.first()
            testcase = TestCase.query.get_or_404(testcase_id)
            project = Project.query.get_or_404(testcase.project_id)

            if project not in g.current_user.followed_projects().all():
                return bad_request('you are not the member of project')

            data = report.to_dict()
            return trueReturn(data, 'found it')

    # 查
    # if operate_type == '2':
    #     if report_id:
    #
    #         # if isinstance(report_id, list):
    #         #     return bad_request('please select one report only to review')
    #
    #         report = Report.query.get_or_404(int(report_id))
    #
    #         # if report.testcase_id != testcase_id:
    #         #     return bad_request('no report %s in testcase %s' % (report.name, testcase.name))
    #         #
    #         # if project not in g.current_user.followed_projects().all():
    #         #     return bad_request('you are not the member of project %s' % project.project_name)
    #
    #         data = report.to_dict()
    #         return trueReturn(data, 'found it')
    #     else:
    #         page_num = int(data.get('page_num', 1))
    #         per_page = int(data.get('per_page', 10))
    #         payload = teststep.to_reports_dict(page_num, per_page)
    #         response = trueReturn(payload, 'list success')
    #         return response

    # 删
    if operate_type == '3':

        if not report_id or not isinstance(report_id, list):
            return bad_request('please select reports to del')

        for id in report_id:
            report = Report.query.get_or_404(id)
            db.session.delete(report)

        session_commit()
        data = {
            'report_id_list': report_id
        }
        response = trueReturn(data, 'delete success')
        return response
