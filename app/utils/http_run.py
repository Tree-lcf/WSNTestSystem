import copy
import json
import datetime

from app.models import *
from httprunner import HttpRunner
from app.common import merge_config
from app.errors import bad_request


def main_ate(tests):
    runner = HttpRunner().run(tests)
    summary = runner.summary
    return summary


class DataExtract:
    def __init__(self, data, make_report=False):
        self.data = data
        self.make_report = make_report

    def project_case(self):
        if self.project_names and not self.scene_ids and not self.case_data:
            scene_id = [s.id for s in Scene.query.filter_by(project_id=self.project_id).order_by(Scene.num.asc()).all()]
            all_case_data = []
            for c in scene_id:
                for c1 in ApiCase.query.filter_by(scene_id=c).order_by(ApiCase.num.asc()).all():
                    all_case_data.append(c1)
            self.run_type = True
            return all_case_data
        else:
            return None

    @staticmethod
    def pro_config(project_data):
        """
        把project的配置数据解析出来
        :param project_data:
        :return:
        """
        pro_cfg_data = {'config': {'name': 'config_name', 'request': {}, 'output': []}, 'teststeps': [],
                        'name': 'config_name'}

        pro_cfg_data['config']['request']['headers'] = {h['key']: h['value'] for h in
                                                        json.loads(project_data.headers) if h.get('key')}

        pro_cfg_data['config']['variables'] = json.loads(project_data.variables)
        return pro_cfg_data

    def extract_data(self):


        temp_case_data = {'name': self.data.name,
                          'request': {'method': self.data.method,
                                      'data': {}}}

        if json.loads(self.data.headers):
            temp_case_data['request']['headers'] = {h['key']: h['value'] for h in json.loads(self.data.headers)
                                                    if h['key']}


        temp_case_data['request']['url'] = data.get('req_temp_host') + '/' + data.get('req_relat_url')

        if api_case.func_address:
            temp_case_data['import_module_functions'] = [
                'func_list.{}'.format(api_case.func_address.replace('.py', ''))]
        # if self.run_type:
        if not self.run_type or json.loads(case_data.status_param)[0]:
            if not self.run_type or json.loads(case_data.status_param)[1]:
                _param = json.loads(case_data.param)

            else:
                _param = json.loads(api_case.param)
            temp_case_data['request']['params'] = {param['key']: param['value'] for param in
                                                   _param if param.get('key')}

        if not self.run_type or json.loads(case_data.status_variables)[0]:
            if not self.run_type or json.loads(case_data.status_variables)[1]:
                _variables = json.loads(case_data.variables)

            else:
                _variables = json.loads(api_case.variables)

            if api_case.variable_type == 'data' and api_case.method != 'GET':
                n = 0
                for variable in _variables:
                    if variable['param_type'] == 'string' and variable.get('key'):
                        temp_case_data['request']['data'].update({variable['key']: variable['value']})
                    elif variable['param_type'] == 'file' and variable.get('key'):
                        temp_case_data['request']['files'].update({variable['key']: (
                            variable['value'].split('/')[-1], open(variable['value'], 'rb'),
                            CONTENT_TYPE['.{}'.format(variable['value'].split('.')[-1])])})
                        # temp_case_data['request']['files'].update({variable['key']: (
                        #     variable['value'].split('/')[-1], "open({}, 'rb')".format(variable['value']),
                        #     CONTENT_TYPE['.{}'.format(variable['value'].split('.')[-1])])})

                        # temp_case_data['request']['files'].update({variable['key']: (
                        #     variable['value'].split('/')[-1], '${' + 'open_file({})'.format(variable['value']) + '}',
                        #     CONTENT_TYPE['.{}'.format(variable['value'].split('.')[-1])])})

            else:
                temp_case_data['request']['json'] = _variables

        if not self.run_type or json.loads(case_data.status_extract)[0]:
            if not self.run_type or json.loads(case_data.status_extract)[1]:
                _extract_temp = case_data.extract
            else:
                _extract_temp = api_case.extract

            temp_case_data['extract'] = [{ext['key']: ext['value']} for ext in json.loads(_extract_temp) if
                                         ext.get('key')]
            self.temp_extract += [ext.get('key') for ext in json.loads(_extract_temp) if ext.get('key')]

        if not self.run_type or json.loads(case_data.status_validate)[0]:
            if not self.run_type or json.loads(case_data.status_validate)[1]:
                _validate_temp = case_data.validate
            else:
                _validate_temp = api_case.validate
            temp_case_data['validate'] = [{val['comparator']: [val['key'], val['value']]} for val in
                                          json.loads(_validate_temp) if val.get('key')]

            temp_case_data['output'] = ['token']

        return temp_case_data

    def all_cases_data(self):
        temp_case = []
        pro_config = self.pro_config(self.project_data)

        # 获取项目中4个基础url
        # pro_base_url = {'0': self.project_data.host, '1': self.project_data.host_two,
        #                 '2': self.project_data.host_three, '3': self.project_data.host_four}
        pro_base_url = {}
        for pro_data in Project.query.all():
            pro_base_url['{}'.format(pro_data.id)] = {'0': pro_data.host, '1': pro_data.host_two,
                                                      '2': pro_data.host_three, '3': pro_data.host_four}

        if self.scene_ids:
            for scene in self.temp_data:
                scene_data = Scene.query.filter_by(id=scene).first()
                scene_times = scene_data.times if scene_data.times else 1
                for s in range(scene_times):
                    _temp_config = copy.deepcopy(pro_config)
                    _temp_config['config']['name'] = scene_data.name

                    # 获取需要导入的函数文件数据
                    _temp_config['config']['import_module_functions'] = ['func_list.{}'.format(
                        scene_data.func_address.replace('.py', ''))] if scene_data.func_address else []

                    # 获取业务集合的配置数据
                    scene_config = json.loads(scene_data.variables) if scene_data.variables else []

                    # 合并公用项目配置和业务集合配置
                    _temp_config = merge_config(_temp_config, scene_config)
                    for case in ApiCase.query.filter_by(scene_id=scene).order_by(ApiCase.num.asc()).all():
                        if case.status == 'true':  # 判断用例状态，是否执行
                            for t in range(case.time):  # 获取用例执行次数，遍历添加
                                _temp_config['teststeps'].append(self.get_case(case, pro_base_url))
                    temp_case.append(_temp_config)
            return temp_case

        if self.case_data:
            _temp_config = copy.deepcopy(pro_config)
            config_data = SceneConfig.query.filter_by(id=self.config_id).first()
            _config = json.loads(config_data.variables) if self.config_id else []
            _temp_config['config']['import_module_functions'] = ['func_list.{}'.format(
                config_data.func_address.replace('.py', ''))] if config_data and config_data.func_address else []

            _temp_config = merge_config(_temp_config, _config)
            _temp_config['teststeps'] = [self.get_case(case, pro_base_url) for case in self.case_data]
            _temp_config['config']['output'] += copy.deepcopy(self.temp_extract)
            return _temp_config
            # return temp_case

    def run_case(self):
        now_time = datetime.datetime.now()

        if self.api_hot_data:


        # if self.test_id and not self.testset_id:
        #     test = Test.query.get_or_404(self.test_id)
        # elif not self.test_id and self.testset_id:
        #     testset = Testset.query.get_or_404(self.testset_id)
        # else:
        #     return bad_request('something wrong on test_id or testset_id')

        if self.run_type and self.make_report:

            new_report = Report(name=,
                                data='{}.txt'.format(now_time.strftime('%Y/%m/%d %H:%M:%S')),
                                belong_pro=self.project_names, read_status='待阅')
            db.session.add(new_report)
            db.session.commit()
        d = self.all_cases_data()
        res = main_ate(d)

        res['time']['duration'] = "%.2f" % res['time']['duration']
        res['stat']['successes_1'] = res['stat']['successes']
        res['stat']['failures_1'] = res['stat']['failures']
        res['stat']['errors_1'] = res['stat']['errors']
        res['stat']['successes'] = "{} ({}%)".format(res['stat']['successes'],
                                                     int(res['stat']['successes'] / res['stat']['testsRun'] * 100))
        res['stat']['failures'] = "{} ({}%)".format(res['stat']['failures'],
                                                    int(res['stat']['failures'] / res['stat']['testsRun'] * 100))
        res['stat']['errors'] = "{} ({}%)".format(res['stat']['errors'],
                                                  int(res['stat']['errors'] / res['stat']['testsRun'] * 100))
        res['stat']['successes_scene'] = 0
        res['stat']['failures_scene'] = 0
        for num_1, res_1 in enumerate(res['details']):
            if res_1['success']:
                res['stat']['successes_scene'] += 1
            else:
                res['stat']['failures_scene'] += 1
            # res_1['in_out']['in'] = res_1['in_out']['in'] if res_1['in_out']['in'] else None
            # res_1['in_out']['out'] = res_1['in_out']['out'] if res_1['in_out']['out'] else None
            for num_2, rec_2 in enumerate(res_1['records']):
                if isinstance(rec_2['meta_data']['response']['content'], bytes):
                    rec_2['meta_data']['response']['content'] = bytes.decode(rec_2['meta_data']['response']['content'])
                if rec_2['meta_data']['request'].get('body'):
                    if isinstance(rec_2['meta_data']['request']['body'], bytes):
                        if b'filename=' in rec_2['meta_data']['request']['body']:
                            rec_2['meta_data']['request']['body'] = '暂不支持显示文件上传的request_body'
                            rec_2['meta_data']['request']['files']['file'] = [0]
                        else:
                            rec_2['meta_data']['request']['body'] = bytes.decode(rec_2['meta_data']['request']['body'])

                if rec_2['meta_data']['request'].get('data'):
                    if isinstance(rec_2['meta_data']['request']['data'], bytes):
                        rec_2['meta_data']['request']['data'] = bytes.decode(rec_2['meta_data']['request']['data'])

                if rec_2['meta_data']['response'].get('cookies'):
                    rec_2['meta_data']['response']['cookies'] = dict(
                        res['details'][0]['records'][0]['meta_data']['response']['cookies'])
                    # for num, rec in enumerate(res['details'][0]['records']):
                    # try:
                    # if not rec['meta_data'].get('url'):
                    #     rec['meta_data']['url'] = self.temporary_url[num] + '\n(url请求失败，这为原始url，)'
                    # if 'Linux' in platform.platform():
                    #     rec['meta_data']['response_time(ms)'] = rec['meta_data'].get('response_time_ms')
                    # if rec['meta_data'].get('response_headers'):
                    #     rec['meta_data']['response_headers'] = dict(res['records'][num]['meta_data']['response_headers'])
                    # if rec['meta_data'].get('request_headers'):
                    #     rec['meta_data']['request_headers'] = dict(res['records'][num]['meta_data']['request_headers'])
                    # if rec['meta_data'].get('request_body'):
                    #     if isinstance(rec['meta_data']['request_body'], bytes):
                    #         if b'filename=' in rec['meta_data']['request_body']:
                    #             rec['meta_data']['request_body'] = '暂不支持显示文件上传的request_body'
                    #         else:
                    #             rec['meta_data']['request_body'] = rec['meta_data']['request_body'].decode('unicode-escape')

                    # if rec['meta_data'].get('response_body'):
                    #     if isinstance(rec['meta_data']['response_body'], bytes):
                    #         rec['meta_data']['response_body'] = bytes.decode(rec['meta_data']['response_body'])
                    # if not rec['meta_data'].get('response_headers'):
                    #     rec['meta_data']['response_headers'] = 'None'

        res['time']['start_at'] = now_time.strftime('%Y/%m/%d %H:%M:%S')
        print(res)
        jump_res = json.dumps(res, ensure_ascii=False)
        if self.run_type and self.make_report:
            self.new_report_id = Report.query.filter_by(
                data='{}.txt'.format(now_time.strftime('%Y/%m/%d %H:%M:%S'))).first().id
            with open('{}{}.txt'.format(REPORT_ADDRESS, self.new_report_id), 'w') as f:
                f.write(jump_res)
        return jump_res
