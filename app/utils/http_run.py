import copy
import json
import datetime

from app.models import *
from httprunner import HttpRunner
from app.common import merge_config, AttrDict, extract_data, MyEncoder, report_minify
from app.errors import bad_request


def main_ate(tests):
    runner = HttpRunner().run(tests)
    summary = runner.summary
    return summary


class Runner:
    def __init__(self, tests, make_report=False):
        self.tests = tests
        self.make_report = make_report
        self.base_payload = {
            'config': {
                'name': 'testcase description',
                'request': {
                    'base_url': '',
                    'headers': {}
                },
                'variables': []
            },
            'teststeps': []
        }

    def load_data(self):
        self.base_payload['teststeps'] = [extract_data(test) for test in self.tests]
        return self.base_payload

    def run(self):
        # now_time = datetime.datetime.now()

        # if self.api_hot_data:
        # if self.test_id and not self.testset_id:
        #     test = Test.query.get_or_404(self.test_id)
        # elif not self.test_id and self.testset_id:
        #     testset = Testset.query.get_or_404(self.testset_id)
        # else:
        #     return bad_request('something wrong on test_id or testset_id')
        #
        # if self.run_type and self.make_report:
        #
        #     new_report = Report(name=,
        #                         data='{}.txt'.format(now_time.strftime('%Y/%m/%d %H:%M:%S')),
        #                         belong_pro=self.project_names, read_status='待阅')
        #     db.session.add(new_report)
        #     db.session.commit()
        payload = self.load_data()
        response = main_ate(payload)
        response = report_minify(response)
        response = json.dumps(response, cls=MyEncoder, indent=4)

        # res['time']['duration'] = "%.2f" % res['time']['duration']
        # res['stat']['successes_1'] = res['stat']['successes']
        # res['stat']['failures_1'] = res['stat']['failures']
        # res['stat']['errors_1'] = res['stat']['errors']
        # res['stat']['successes'] = "{} ({}%)".format(res['stat']['successes'],
        #                                              int(res['stat']['successes'] / res['stat']['testsRun'] * 100))
        # res['stat']['failures'] = "{} ({}%)".format(res['stat']['failures'],
        #                                             int(res['stat']['failures'] / res['stat']['testsRun'] * 100))
        # res['stat']['errors'] = "{} ({}%)".format(res['stat']['errors'],
        #                                           int(res['stat']['errors'] / res['stat']['testsRun'] * 100))
        # res['stat']['successes_scene'] = 0
        # res['stat']['failures_scene'] = 0
        # for num_1, res_1 in enumerate(res['details']):
        #     if res_1['success']:
        #         res['stat']['successes_scene'] += 1
        #     else:
        #         res['stat']['failures_scene'] += 1
        #
        #     for num_2, rec_2 in enumerate(res_1['records']):
        #         if isinstance(rec_2['meta_data']['response']['content'], bytes):
        #             rec_2['meta_data']['response']['content'] = bytes.decode(rec_2['meta_data']['response']['content'])
        #         if rec_2['meta_data']['request'].get('body'):
        #             if isinstance(rec_2['meta_data']['request']['body'], bytes):
        #                 if b'filename=' in rec_2['meta_data']['request']['body']:
        #                     rec_2['meta_data']['request']['body'] = '暂不支持显示文件上传的request_body'
        #                     rec_2['meta_data']['request']['files']['file'] = [0]
        #                 else:
        #                     rec_2['meta_data']['request']['body'] = bytes.decode(rec_2['meta_data']['request']['body'])
        #
        #         if rec_2['meta_data']['request'].get('data'):
        #             if isinstance(rec_2['meta_data']['request']['data'], bytes):
        #                 rec_2['meta_data']['request']['data'] = bytes.decode(rec_2['meta_data']['request']['data'])
        #
        #         if rec_2['meta_data']['response'].get('cookies'):
        #             rec_2['meta_data']['response']['cookies'] = dict(
        #                 res['details'][0]['records'][0]['meta_data']['response']['cookies'])
        #
        #
        # res['time']['start_at'] = now_time.strftime('%Y/%m/%d %H:%M:%S')
        # if self.run_type and self.make_report:
        #     self.new_report_id = Report.query.filter_by(
        #         data='{}.txt'.format(now_time.strftime('%Y/%m/%d %H:%M:%S'))).first().id
        #     with open('{}{}.txt'.format(REPORT_ADDRESS, self.new_report_id), 'w') as f:
        #         f.write(jump_res)
        return response
