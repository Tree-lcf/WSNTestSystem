from httprunner import HttpRunner
import threading
from app.models import *


def main_ate(tests):
    # print(tests)
    runner = HttpRunner().run(tests)
    summary = runner.summary
    return summary


class Runner:
    def __init__(self, tests, config=None, make_report=False):
        self.tests = tests
        self.config = config
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
        if not self.config:
            self.base_payload['teststeps'] = [extract_data(test) for test in self.tests]
        else:
            self.base_payload['config'] = self.config
            self.base_payload['teststeps'] = [extract_data(test) for test in self.tests]
        return self.base_payload

    def run(self):
        payload = self.load_data()
        response = main_ate(payload)
        response = report_minify(response)
        response = json.dumps(response, cls=MyEncoder, indent=4)

        return response


def session_commit():
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        reason = str(e)
        return reason


class AttrDict(dict):
    """
    A class to convert a nested Dictionary into an object with key-values
    that are accessible using attribute notation (AttrDict.attribute) instead of
    key notation (Dict["key"]). This class recursively sets Dicts to objects,
    allowing you to recurse down nested dicts (like: AttrDict.attr.attr)
    """

    # Inspired by:
    # http://stackoverflow.com/a/14620633/1551810
    # http://databio.org/posts/python_AttributeDict.html

    def __init__(self, iterable, **kwargs):
        super(AttrDict, self).__init__(iterable, **kwargs)
        for key, value in iterable.items():
            if isinstance(value, dict):
                self.__dict__[key] = AttrDict(value)
            else:
                self.__dict__[key] = value


def check_repeat(origin_list):
    _list = origin_list.copy()
    new_list = list(set(_list))

    for a in new_list:
        if a in _list:
            _list.remove(a)

    return _list


def extract_data(test_data):
    test_data = AttrDict(test_data)
    payload = {
        'name': test_data.name,
        'request': {
            'method': test_data['req_method']
        }
    }

    if test_data.req_headers:
        payload['request']['headers'] = json.loads(test_data.req_headers)

    if test_data.req_cookies:
        payload['request']['cookies'] = json.loads(test_data.req_cookies)

    payload['request']['url'] = test_data.get('req_temp_host') + '/' + test_data.get('req_relate_url')

    if test_data.req_params:
        payload['request']['params'] = json.loads(test_data.req_params)

    if test_data.get('req_data_type') == 'data':
        payload['request']['data'] = json.loads(test_data.req_body)

    if test_data.get('req_data_type') == 'json':
        payload['request']['json'] = json.loads(test_data.req_body)

    if test_data.extracts:
        payload['extract'] = json.loads(test_data.extracts)

    if test_data.asserts:
        payload['validate'] = json.loads(test_data.asserts)

    if test_data.variables:
        payload['variables'] = json.loads(test_data.variables)

    return payload


class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytes):
            return str(obj, encoding='utf-8')
        return json.JSONEncoder.default(self, obj)


def report_minify(report):
    report = report
    report.pop('platform')
    report['details'][0].pop('time')
    report['details'][0].pop('base_url')
    report['details'][0].pop('in_out')
    report['details'][0].pop('stat')
    report['details'][0]['records'][0].pop('attachment')
    report['details'][0]['records'][0]['meta_data']['response'].pop('reason')
    report['details'][0]['records'][0]['meta_data']['response'].pop('text')
    report['details'][0]['records'][0]['meta_data']['response'].pop('url')
    report['details'][0]['records'][0]['meta_data']['response'].pop('content')
    report['details'][0]['records'][0]['meta_data']['response'].pop('content_size')
    report['details'][0]['records'][0]['meta_data']['response'].pop('encoding')
    report['details'][0]['records'][0]['meta_data']['response'].pop('response_time_ms')

    return report


class MyThread(threading.Thread):

    def __init__(self, func, args=(), name=''):
        threading.Thread.__init__(self)
        self.name = name
        self.func = func
        self.args = args
        self.result = self.func(*self.args)

    def run(self):
        self.func(*self.args)

    def get_result(self):
        try:
            return self.result
        except Exception:
            return None


class RunJob:
    def __init__(self, payload, config):
        self.payload = payload
        self.config = config

    def run(self):

        tester = Runner(self.payload, self.config)
        result = tester.run()
        result = json.loads(result)

        return result

    def job(self):
        thread = MyThread(self.run, name=self.run.__name__)
        thread.start()
        thread.join()
        return thread.get_result()


def to_obj(data):
    payload = []
    for obj in json.loads(data):
        for item, value in obj.items():
            obj_t = {
                'key': item,
                'value': value
            }
            payload.append(obj_t)
    return payload


def to_obj_2(data):
    payload = []
    for obj in json.loads(data):
        for item, value in obj.items():
            obj_t = {
                'eq': item,
                'actual': value[0],
                'expect': value[1]
            }
            payload.append(obj_t)
    return payload


def objlist_to_str(data):
        payload = {}
        for obj in data:
            obj_t = {obj['key']: obj['value']}
            payload = dict(payload, **obj_t)

        payload_tostr = json.dumps(payload)
        return payload_tostr


if __name__ == '__main__':
    a = [{'key': 'token', 'value': 'ew6gouhgUrHP0ayeQIAGAcFQnQCNg/xT'}]
    b = objlist_to_str(a)
    print(b)

