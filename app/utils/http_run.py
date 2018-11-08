# from app.models import *
# from httprunner import HttpRunner
# from app.common import extract_data, MyEncoder, report_minify
#
#
# def main_ate(tests):
#     runner = HttpRunner().run(tests)
#     summary = runner.summary
#     return summary
#
#
# class Runner:
#     def __init__(self, tests, config=None, make_report=False):
#         self.tests = tests
#         self.config = config
#         self.make_report = make_report
#         self.base_payload = {
#             'config': {
#                 'name': 'testcase description',
#                 'request': {
#                     'base_url': '',
#                     'headers': {}
#                 },
#                 'variables': []
#             },
#             'teststeps': []
#         }
#
#     def load_data(self):
#         if not self.config:
#             self.base_payload['teststeps'] = [extract_data(test) for test in self.tests]
#         else:
#             self.base_payload['config'] = self.config
#             self.base_payload['teststeps'] = [extract_data(test) for test in self.tests]
#         return self.base_payload
#
#     def run(self):
#         payload = self.load_data()
#         response = main_ate(payload)
#         response = report_minify(response)
#         response = json.dumps(response, cls=MyEncoder, indent=4)
#
#         return response
