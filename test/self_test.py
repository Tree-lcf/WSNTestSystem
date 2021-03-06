import unittest
import requests
from app import create_app, db
from app.models import User, Project, Module, Env, Api, TestCase, TestStep, Report
from config import Config
from app.common import AttrDict


class TestRestApiCase(unittest.TestCase):

    # @classmethod
    # def setUpClass(cls):
    #     cls.app = create_app(Config)
    #     cls.app_context = cls.app.app_context()
    #     cls.app_context.push()
    #     cls.reg_data = {
    #         'username': '003',
    #         'email': '003@wsn.cn',
    #         'password': '123'
    #     }
    #     host = 'http://127.0.0.1:5000'
    #     cls.register_url = host + '/auth/register'
    #     cls.login_url = host + '/auth/login'
    #
    # @classmethod
    # def tearDownClass(cls):
    #     db.session.remove()
    #     user = User.query.filter_by(username='003').first()
    #     try:
    #         db.session.delete(user)
    #         db.session.commit()
    #     except Exception:
    #         pass
    #
    #     cls.app_context.pop()

    def setUp(self):
        self.app = create_app(Config)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.reg_data = {
            'username': '003',
            'email': '003@wsn.cn',
            'password': '123'
        }
        self.reg_data_copy = {
            'username': '007',
            'email': '007@wsn.cn',
            'password': '123'
        }
        self.login_data = {
            'username': '003',
            'password': '123'
        }
        self.module_data = {
            'module_name': 'app_module_1',
            'project_name': 'app'
        }
        self.module_data_copy = {
            'module_name': 'app_module_2',
            'project_name': 'app'
        }
        self.module_info = {
            'project_name': 'app',
            'update_info_list': [{'origin_name': 'app_module_1', 'new_name': 'aa'}]
        }
        self.moduleOperate_1 = {
            'project_id': 'app',
            'module_name': 'app_module_1',
            'origin_name': None,
            'operate_type': '1'
        }
        self.moduleOperate_1_1 = {
            'project_name': 'app',
            'module_name': 'app_module_2',
            'origin_name': None,
            'operate_type': '1'
        }
        self.moduleOperate_2 = {
            'project_name': 'app',
            'module_name': 'aa',
            'origin_name': 'app_module_1',
            'operate_type': '2'
        }
        self.moduleOperate_3 = {
            'project_name': 'app',
            'module_name': None,
            'origin_name': None,
            'operate_type': '3'
        }
        self.moduleOperate_4 = {
            'project_name': 'app',
            'module_name': None,
            'origin_name': 'app_module_2',
            'operate_type': '4'
        }
        self.envOperate_1 = {
            'project_id': '1',
            'env_name': 'env_1',
            'env_id': 1,
            'env_desc': '1',
            'operate_type': '1',
            'page_num': '1',
            'per_page': '10',
            'env_host': '127.0.0.1',
            'env_var': 'uuid = 123',
            'extracts': '[1, 2]',
            'asserts': '[True, False]'
        }
        self.envOperate_1_1 = {
            'project_id': 'app',
            'env_id': None,
            'env_name': 'env_2',
            'env_desc': '2',
            'operate_type': '1',
            'page_num': None,
            'per_page': None,
            'env_host': 'http://61.160.64.130:8081',
            'env_var': [{"key": "uuid", 'value': "24FB4CCC-75AD-49D5-9937-0402E3A6C8E0"}, {'key': "passWord", 'value': "Jfpt123456"}],
            'extracts': [{'key': "kaptcha", 'value': "json.responseData.kaptcha"}],
            'asserts': [{'eq': "eq", 'actual': "json.retCode", 'expect': "0"}]
        }
        self.envOperate_1_2 = {
            'project_id': 'app',
            'env_id': None,
            'env_name': 'env_2-1',
            'env_desc': '2',
            'operate_type': '1',
            'page_num': None,
            'per_page': None,
            'env_host': '',
            'env_var': '',
            'extracts': [{'key': "kaptcha", 'value': "json.responseData.sessionID"}],
            'asserts': [{'eq': "eq", 'actual': "json.retCode", 'expect': "0"}]
        }
        self.envOperate_1_3 = {
            'project_id': 'app',
            'env_id': None,
            'env_name': 'env_2-2',
            'env_desc': '3',
            'operate_type': '1',
            'page_num': None,
            'per_page': None,
            'env_host': 'http://61.160.64.130:8081',
            'env_var': '[{"type": "ios"}]',
            'extracts': '[{"kaptcha": "json.responseData.info.latest"}]',
            'asserts': '[{"eq": ["json.retCode", "0"]}]'
        }
        self.envOperate_3 = {
            'project_id': None,
            'env_id': None,
            'env_name': None,
            'env_desc': None,
            'operate_type': '3',
            'page_num': '1',
            'per_page': '20',
        }
        self.envOperate_2 = {
            'project_id': None,
            'env_id': None,
            'env_name': 'aa',
            'env_desc': '1',
            'operate_type': '2',
            'page_num': None,
            'per_page': None,
        }
        self.envOperate_4 = {
            'project_id': None,
            'env_id': None,
            'env_name': None,
            'env_desc': None,
            'operate_type': '4',
            'page_num': None,
            'per_page': None,
        }
        self.apiOperate_1 = {
            'project_id': 1,
            'module_id': 1,
            'name': 'api_1',
            'api_id': 1,
            'req_method': 'req_method',
            'req_temp_host': 'req_temp_host',
            'req_relate_url': 'req_relate_url',
            'req_headers': 'req_headers',
            'req_params': 'req_params',
            'req_data_type': 'req_data_type',
            'req_body': 'req_body',
            'operate_type': '1',
            'page_num': 1,
            'per_page': 20
        }
        self.apiOperate_2 = {
            'project_id': 1,
            'module_id': 1,
            'name': 'api_2',
            'api_id': 1,
            'req_method': '2',
            'req_temp_host': '2',
            'req_relate_url': '2',
            'req_headers': '2',
            'req_params': '2',
            'req_data_type': '2',
            'req_body': '2',
            'operate_type': '2',
            'page_num': None,
            'per_page': None
        }
        self.apiOperate_5 = {
            'project_id': 1,
            'module_id': 1,
            'name': 'api_2',
            'api_id': 1,
            'req_method': 'POST',
            'req_temp_host': '',
            'req_relate_url': 'getKaptcha',
            'req_headers': '{"Content-Type": "application/json"}',
            'req_cookies': '',
            'req_params': '',
            'req_data_type': 'json',
            'req_body': '',
            'extracts': '[]',
            'asserts': '',
            'variables': '',
            'operate_type': '5',
            'page_num': None,
            'per_page': None
        }
        self.apiOperate_11 = {
            'project_id': 1,
            'module_id': 1,
            'name': 'api_2',
            'api_id': 1,
            'req_method': 'POST',
            'req_temp_host': 'http://61.160.64.130:8081',
            'req_relate_url': 'getKaptcha',
            'req_headers': '{"Content-Type": "application/json"}',
            'req_cookies': '',
            'req_params': '',
            'req_data_type': 'json',
            'req_body': '{"uuid": "24FB4CCC-75AD-49D5-9937-0402E3A6C8E0"}',
            'extracts': '',
            'asserts': '',
            'variables': '',
            'operate_type': '5',
            'page_num': None,
            'per_page': None
        }
        self.apiOperate_6 = {
            'project_id': 1,
            'module_id': 1,
            'name': 'api_6',
            'api_id': 1,
            'req_method': 'POST',
            'req_temp_host': '',
            'req_relate_url': 'login',
            'req_headers': '{"Content-Type": "application/json"}',
            'req_cookies': '',
            'req_params': '',
            'req_data_type': 'json',
            'req_body': '',
            'extracts': '',
            'asserts': '',
            'variables': '',
            'operate_type': '1',
            'page_num': None,
            'per_page': None
        }
        self.apiOperate_7 = {
            'project_id': 1,
            'module_id': 1,
            'name': 'api_7',
            'api_id': 1,
            'req_method': 'POST',
            'req_temp_host': '',
            'req_relate_url': 'msg/getVersionInfo',
            'req_headers': '{"Content-Type": "application/json"}',
            'req_cookies': '',
            'req_params': '',
            'req_data_type': 'json',
            'req_body': '',
            'extracts': '',
            'asserts': '',
            'variables': '',
            'operate_type': '1',
            'page_num': None,
            'per_page': None
        }
        self.testcaseOperate_1 = {
            'project_id': 1,
            'api_id': 1,
            'testcase_id': 1,
            'env_id': 1,
            'name': 'test_1',
            'test_desc': 'test_desc',
            'teststeps': '[{teststep}, {teststep}]',
            'operate_type': '1',
            'page_num': 1,
            'per_page': 10
        }
        self.teststepOperate_1 = {
            'api_id': 1,
            'env_id': 1,
            'teststep_id': 1,
            'name': 'teststep_1',
            'req_headers': '',
            'req_params': '',
            'req_body': '{"uuid": "$uuid"}',
            'req_cookies': '',
            'operate_type': '1',
        }
        self.teststepOperate_2 = {
            'api_id': 1,
            'env_id': 1,
            'teststep_id': 1,
            'name': 'teststep_2',
            'req_headers': '',
            'req_params': '',
            'req_body': '{"userName": "jsyh01","kaptcha": "$kaptcha",'
                        '"uuid": "$uuid","type": "2","appVersion": "V1.3.1(IOS)",'
                        '"passWord": "$passWord"}',
            'req_cookies': '',
            'operate_type': '1',
        }
        self.teststepOperate_3 = {
            'api_id': 1,
            'env_id': 1,
            'teststep_id': 1,
            'name': 'teststep_3',
            'req_headers': '',
            'req_params': '',
            'req_body': '{"type": "$type"}',
            'req_cookies': '',
            'operate_type': '1',
        }
        self.testsBatchRun_1 = {
            'project_id': 1,
            'test_id_items': []
        }
        self.report_1 = {
            'testcase_id': 1,
            'report_id': 1,  # int or list of int
            'operate_type': '2',
            'page_num': 1,
            'per_page': 10
        }

        host = 'http://127.0.0.1:5000'
        # host = 'http://192.168.2.150:5000'
        self.register_url = host + '/auth/register'
        self.login_url = host + '/auth/login'
        self.logout_url = host + '/auth/logout'
        self.get_projects_url = host + '/api/projectsList'
        self.add_project_url = host + '/api/projectCreate'
        self.project_has_user_url = host + '/api/projectLinkUser'
        self.get_project_url = host + '/api/projectInfo'
        self.del_project_url = host + '/api/projectDel'
        self.update_project_url = host + '/api/projectUpdate'
        self.get_users_url = host + '/api/users'
        self.create_module_url = host + '/api/moduleCreate'
        self.del_module_url = host + '/api/modulesDel'
        self.update_module_url = host + '/api/modulesUpdate'
        self.get_modules_url = host + '/api/moduleList'
        self.moduleOperate_url = host + '/api/moduleOperate'
        self.envOperate_url = host + '/api/envOperate'
        self.apiOperate_url = host + '/api/apiOperate'
        self.testCaseOperate_url = host + '/api/testCaseOperate'
        self.testStepOperate_url = host + '/api/testStepOperate'
        self.testsBatchRun_url = host + '/api/testsBatchRun'
        self.report_url = host + '/api/report'

    def tearDown(self):
        db.session.remove()
        users = User.query.all()
        projects = Project.query.all()
        modules = Module.query.all()
        envs = Env.query.all()
        apis = Api.query.all()
        testcases = TestCase.query.all()
        teststeps = TestStep.query.all()
        reports = Report.query.all()

        for user in users:
            db.session.delete(user)

        for project in projects:
            db.session.delete(project)

        for module in modules:
            db.session.delete(module)

        for env in envs:
            db.session.delete(env)

        for api in apis:
            db.session.delete(api)

        for testcase in testcases:
            db.session.delete(testcase)

        for teststep in teststeps:
            db.session.delete(teststep)

        for report in reports:
            db.session.delete(report)

        db.session.commit()

        self.app_context.pop()

    def test_register_success(self):
        response = requests.post(self.register_url, json=self.reg_data).json()
        response = AttrDict(response)
        self.assertTrue(response.status)
        self.assertEqual(response.data.username, '003')

    def test_register_fail(self):
        del self.reg_data['password']
        response = requests.post(self.register_url, json=self.reg_data).json()
        response = AttrDict(response)
        self.assertFalse(response.status)
        self.assertEqual(response.error, 'Bad Request')

    def test_login_success(self):
        requests.post(self.register_url, json=self.reg_data)
        response = requests.post(self.login_url, json=self.login_data).json()
        response = AttrDict(response)
        self.assertTrue(response.status)
        self.assertEqual(response.data.username, '003')
        self.assertIsNotNone(response.data.token)

    def test_login_fail(self):
        del self.login_data['password']
        requests.post(self.register_url, json=self.reg_data)
        response = requests.post(self.login_url, json=self.login_data).json()
        response = AttrDict(response)
        self.assertFalse(response.status)
        self.assertEqual(response.error, 'Bad Request')

    def test_login_Unauthorized(self):
        requests.post(self.register_url, json=self.reg_data)
        self.login_data['password'] = '456'
        response = requests.post(self.login_url, json=self.login_data).json()
        response = AttrDict(response)
        self.assertFalse(response.status)
        self.assertEqual(response.error, 'Unauthorized')

    def test_login_out(self):
        requests.post(self.register_url, json=self.reg_data)
        response = requests.post(self.login_url, json=self.login_data).json()
        response = AttrDict(response)
        cookies = {'token': response.data.token}
        response = requests.get(self.logout_url, cookies=cookies).json()
        response = AttrDict(response)
        print(response)
        self.assertTrue(response.status)

    def test_login_out_fail(self):
        cookies = {'token': ''}
        response = requests.get(self.logout_url, cookies=cookies).json()
        response = AttrDict(response)
        print(response)
        self.assertFalse(response.status)

    def test_getProjectList_success(self):
        requests.post(self.register_url, json=self.reg_data)
        response = requests.post(self.login_url, json=self.login_data).json()
        response = AttrDict(response)
        cookies = {'token': response.data.token}
        payload = {
            'project_name': 'app',
            'owner_name': ['003']
        }
        requests.post(self.add_project_url, cookies=cookies, json=payload)
        payload = {'page_num': '1', 'per_page': '20'}
        response = requests.get(self.get_projects_url, cookies=cookies, params=payload).json()
        response = AttrDict(response)
        print(response)
        self.assertTrue(response.status)
        self.assertTrue(len(response.data.project_items) > 0)

    def test_getProjectList_fail(self):
        cookies = {'token': '123'}
        response = requests.get(self.get_projects_url, cookies=cookies).json()
        response = AttrDict(response)
        self.assertFalse(response.status)

    def test_add_Project_success(self):
        requests.post(self.register_url, json=self.reg_data)
        response = requests.post(self.login_url, json=self.login_data).json()
        response = AttrDict(response)
        cookies = {'token': response.data.token}
        payload = {
            'project_name': 'app',
            'owner_name': '003'
        }
        response = requests.post(self.add_project_url, cookies=cookies, json=payload).json()
        response = AttrDict(response)
        print(response)
        self.assertTrue(response.status)
        self.assertEqual(response.data.project_name, 'app')

    def test_project_has_user_success(self):
        requests.post(self.register_url, json=self.reg_data)
        response = requests.post(self.login_url, json=self.login_data).json()
        response = AttrDict(response)
        cookies = {'token': response.data.token}
        payload = {
            'project_name': 'app',
            'owner_name': '003'
        }
        response = requests.post(self.add_project_url, cookies=cookies, json=payload).json()
        response = AttrDict(response)
        project_id = response.data.project_id
        requests.post(self.register_url, json=self.reg_data_copy)
        payload = {
            'project_id': project_id,
            'username_list': ['007'],
            'follow_type': '1'
        }

        response = requests.post(self.project_has_user_url, cookies=cookies, json=payload).json()
        response = AttrDict(response)
        print(response)
        self.assertTrue(response.status)

    def test_project_has_user_fail_no_user(self):
        requests.post(self.register_url, json=self.reg_data)
        response = requests.post(self.login_url, json=self.login_data).json()
        response = AttrDict(response)
        cookies = {'token': response.data.token}
        payload = {
            'project_name': 'app',
            'owner_name': '003'
        }
        requests.post(self.add_project_url, cookies=cookies, json=payload)

        payload = {
            'project_name': 'app',
            'username_list': ['007'],
            'follow_type': '1'
        }
        response = requests.post(self.project_has_user_url, cookies=cookies, json=payload).json()
        response = AttrDict(response)
        print(response)
        self.assertFalse(response.status)

    def test_project_has_user_fail_no_project(self):
        requests.post(self.register_url, json=self.reg_data)
        response = requests.post(self.login_url, json=self.login_data).json()
        response = AttrDict(response)
        cookies = {'token': response.data.token}
        payload = {
            'project_name': 'app',
            'owner_name': '003'
        }
        requests.post(self.add_project_url, cookies=cookies, json=payload)

        payload = {
            'project_name': 'app1',
            'username_list': ['006'],
            'follow_type': '1'
        }
        response = requests.post(self.project_has_user_url, cookies=cookies, json=payload).json()
        response = AttrDict(response)
        print(response)
        self.assertFalse(response.status)

    def test_project_has_user_fail_already_exist(self):
        requests.post(self.register_url, json=self.reg_data)
        response = requests.post(self.login_url, json=self.login_data).json()
        response = AttrDict(response)
        cookies = {'token': response.data.token}
        payload = {
            'project_name': 'app',
            'owner_name': '003'
        }
        requests.post(self.add_project_url, cookies=cookies, json=payload)
        requests.post(self.register_url, json=self.reg_data_copy)
        payload = {
            'project_name': 'app',
            'username_list': ['007'],
            'follow_type': '1'
        }
        requests.post(self.project_has_user_url, cookies=cookies, json=payload)
        payload = {
            'project_name': 'app',
            'username_list': ['007'],
            'follow_type': '1'
        }
        response = requests.post(self.project_has_user_url, cookies=cookies, json=payload).json()
        response = AttrDict(response)
        print(response)
        self.assertFalse(response.status)

    def test_project_has_user_fail_same_owner(self):
        requests.post(self.register_url, json=self.reg_data)
        response = requests.post(self.login_url, json=self.login_data).json()
        response = AttrDict(response)
        cookies = {'token': response.data.token}
        payload = {
            'project_name': 'app',
            'owner_name': '003'
        }
        requests.post(self.add_project_url, cookies=cookies, json=payload)

        payload = {
            'project_name': 'app',
            'username_list': ['003'],
            'follow_type': '1'
        }
        response = requests.post(self.project_has_user_url, cookies=cookies, json=payload).json()
        response = AttrDict(response)
        print(response)
        self.assertFalse(response.status)

    def test_project_unfollow_user_success(self):
        requests.post(self.register_url, json=self.reg_data)
        response = requests.post(self.login_url, json=self.login_data).json()
        response = AttrDict(response)
        cookies = {'token': response.data.token}
        payload = {
            'project_name': 'app',
            'owner_name': '003'
        }
        response = requests.post(self.add_project_url, cookies=cookies, json=payload).json()
        response = AttrDict(response)
        project_id = response.data.project_id
        requests.post(self.register_url, json=self.reg_data_copy)
        payload = {
            'project_id': project_id,
            'username_list': ['007'],
            'follow_type': '1'
        }
        response = requests.post(self.project_has_user_url, cookies=cookies, json=payload).json()
        print(response)
        payload = {
            'project_id': project_id,
            'username_list': ['007'],
            'follow_type': '2'
        }
        response = requests.post(self.project_has_user_url, cookies=cookies, json=payload).json()
        response = AttrDict(response)
        print(response)
        self.assertTrue(response.status)

    def test_project_unfollow_user_fail(self):
        requests.post(self.register_url, json=self.reg_data)
        response = requests.post(self.login_url, json=self.login_data).json()
        response = AttrDict(response)
        cookies = {'token': response.data.token}
        payload = {
            'project_name': 'app',
            'owner_name': '003'
        }
        requests.post(self.add_project_url, cookies=cookies, json=payload)
        requests.post(self.register_url, json=self.reg_data_copy)
        payload = {
            'project_name': 'app',
            'username_list': ['007'],
            'follow_type': '1'
        }
        response = requests.post(self.project_has_user_url, cookies=cookies, json=payload).json()
        print(response)
        payload = {
            'project_name': 'app',
            'username_list': ['007'],
            'follow_type': '3'
        }
        response = requests.post(self.project_has_user_url, cookies=cookies, json=payload).json()
        response = AttrDict(response)
        print(response)
        self.assertFalse(response.status)

    def test_getProject_success(self):
        requests.post(self.register_url, json=self.reg_data)
        response = requests.post(self.login_url, json=self.login_data).json()
        response = AttrDict(response)
        cookies = {'token': response.data.token}
        payload = {
            'project_name': 'app',
            'owner_name': '003'
        }
        requests.post(self.add_project_url, cookies=cookies, json=payload)
        payload = {
            'project_name': 'app'
        }
        response = requests.get(self.get_project_url, cookies=cookies, params=payload).json()
        response = AttrDict(response)
        print(response)
        self.assertTrue(response.status)
        self.assertTrue(len(response.data) > 0)

    def test_getProject_fail(self):
        requests.post(self.register_url, json=self.reg_data)
        response = requests.post(self.login_url, json=self.login_data).json()
        response = AttrDict(response)
        cookies = {'token': response.data.token}
        payload = {
            'project_name': 'app',
            'owner_name': '003'
        }
        requests.post(self.add_project_url, cookies=cookies, json=payload)
        payload = {'project_name': 'aa'}
        response = requests.get(self.get_project_url, cookies=cookies, params=payload).json()
        response = AttrDict(response)
        print(response)
        self.assertFalse(response.status)

    def test_projectDel_success(self):
        requests.post(self.register_url, json=self.reg_data)
        response = requests.post(self.login_url, json=self.login_data).json()
        response = AttrDict(response)
        cookies = {'token': response.data.token}
        payload = {
            'project_name': 'app',
            'owner_name': '003'
        }
        response = requests.post(self.add_project_url, cookies=cookies, json=payload).json()
        response = AttrDict(response)
        project_id = response.data.project_id
        payload = {'project_id': project_id}
        response = requests.post(self.del_project_url, cookies=cookies, json=payload).json()
        response = AttrDict(response)
        print(response)
        self.assertTrue(response.status)

    def test_projectDel_fail_not_owner(self):
        requests.post(self.register_url, json=self.reg_data)
        requests.post(self.register_url, json=self.reg_data_copy)
        response = requests.post(self.login_url, json=self.login_data).json()
        response = AttrDict(response)
        cookies = {'token': response.data.token}
        payload = {
            'project_name': 'app',
            'owner_name': '007'
        }
        requests.post(self.add_project_url, cookies=cookies, json=payload)
        payload = {'project_name': 'app'}
        response = requests.post(self.del_project_url, cookies=cookies, json=payload).json()
        response = AttrDict(response)
        print(response)
        self.assertFalse(response.status)

    def test_update_project_success(self):
        requests.post(self.register_url, json=self.reg_data)
        requests.post(self.register_url, json=self.reg_data_copy)
        response = requests.post(self.login_url, json=self.login_data).json()
        response = AttrDict(response)
        cookies = {'token': response.data.token}
        payload = {
            'project_name': 'app',
            'owner_name': '003'
        }
        response = requests.post(self.add_project_url, cookies=cookies, json=payload).json()
        response = AttrDict(response)
        origin_project_id = response.data.project_id
        payload = {
            'project_name': 'cpp',
            'owner_name': '007',
            'origin_project_id': origin_project_id,
            'origin_owner_name': '003'
        }
        response = requests.post(self.update_project_url, cookies=cookies, json=payload).json()
        response = AttrDict(response)
        print(response)
        self.assertTrue(response.status)

    def test_update_project_fail(self):
        requests.post(self.register_url, json=self.reg_data)
        requests.post(self.register_url, json=self.reg_data_copy)
        response = requests.post(self.login_url, json=self.login_data).json()
        response = AttrDict(response)
        cookies = {'token': response.data.token}
        payload = {
            'project_name': 'app',
            'owner_name': '003'
        }
        requests.post(self.add_project_url, cookies=cookies, json=payload)
        payload = {
            'project_name': 'cpp',
            'owner_name': '006',
            'origin_project_name': 'app',
            'origin_owner_name': '003'
        }
        response = requests.post(self.update_project_url, cookies=cookies, json=payload).json()
        response = AttrDict(response)
        print(response)
        self.assertFalse(response.status)

    def test_get_users_success(self):
        requests.post(self.register_url, json=self.reg_data)
        requests.post(self.register_url, json=self.reg_data_copy)
        response = requests.post(self.login_url, json=self.login_data).json()
        response = AttrDict(response)
        cookies = {'token': response.data.token}
        # payload = {'page_num': '1', 'per_page': '20'}
        response = requests.get(self.get_users_url, cookies=cookies).json()
        response = AttrDict(response)
        print(response)
        self.assertTrue(response.status)

    def test_get_modules_success1(self):
        requests.post(self.register_url, json=self.reg_data)
        response = requests.post(self.login_url, json=self.login_data).json()
        response = AttrDict(response)
        cookies = {'token': response.data.token}
        payload = {
            'project_name': 'app',
            'owner_name': '003'
        }
        requests.post(self.add_project_url, cookies=cookies, json=payload)
        response = requests.post(self.create_module_url, cookies=cookies, json=self.module_data).json()
        print(response)
        requests.post(self.create_module_url, cookies=cookies, json=self.module_data_copy)
        response = requests.post(self.get_modules_url, cookies=cookies, json=self.module_data).json()
        print(response)
        response = requests.post(self.del_module_url, cookies=cookies, json=self.module_data_copy).json()
        print(response)
        response = requests.post(self.update_module_url, cookies=cookies, json=self.module_info).json()
        print(response)

    def test_operate_modules_success(self):
        requests.post(self.register_url, json=self.reg_data)
        response = requests.post(self.login_url, json=self.login_data).json()
        response = AttrDict(response)
        cookies = {'token': response.data.token}
        payload = {
            'project_name': 'app',
            'owner_name': '003'
        }
        requests.post(self.add_project_url, cookies=cookies, json=payload)

        response = requests.post(self.moduleOperate_url, cookies=cookies, json=self.moduleOperate_1).json()
        response = AttrDict(response)
        print(response)
        self.assertTrue(response.status)
        response = requests.post(self.moduleOperate_url, cookies=cookies, json=self.moduleOperate_1_1).json()
        response = AttrDict(response)
        print(response)
        self.assertTrue(response.status)
        response = requests.post(self.moduleOperate_url, cookies=cookies, json=self.moduleOperate_3).json()
        response = AttrDict(response)
        print(response)
        self.assertTrue(response.status)
        response = requests.post(self.moduleOperate_url, cookies=cookies, json=self.moduleOperate_4).json()
        response = AttrDict(response)
        print(response)
        self.assertTrue(response.status)
        response = requests.post(self.moduleOperate_url, cookies=cookies, json=self.moduleOperate_2).json()
        response = AttrDict(response)
        print(response)
        self.assertTrue(response.status)

    def test_operate_envs_success(self):
        requests.post(self.register_url, json=self.reg_data)
        response = requests.post(self.login_url, json=self.login_data).json()
        response = AttrDict(response)
        cookies = {'token': response.data.token}
        payload = {
            'project_name': 'app',
            'owner_name': '003'
        }
        response = requests.post(self.add_project_url, cookies=cookies, json=payload).json()
        response = AttrDict(response)

        project_id = response.data.project_id
        self.envOperate_1_1['project_id'] = project_id
        response = requests.post(self.envOperate_url, cookies=cookies, json=self.envOperate_1_1).json()
        response = AttrDict(response)
        print('----- add -----')
        print(response)
        self.assertTrue(response.status)

        self.envOperate_1['project_id'] = project_id
        response = requests.post(self.envOperate_url, cookies=cookies, json=self.envOperate_1).json()
        response = AttrDict(response)
        print('----- add -----')
        print(response)
        self.assertTrue(response.status)
        self.envOperate_3['env_id'] = response.data.env_id
        response = requests.post(self.envOperate_url, cookies=cookies, json=self.envOperate_3).json()
        response = AttrDict(response)
        print('----- found -----')
        print(response)
        self.assertTrue(response.status)
        self.envOperate_2['env_id'] = response.data.env_id
        self.envOperate_4['env_id'] = response.data.env_id
        response = requests.post(self.envOperate_url, cookies=cookies, json=self.envOperate_2).json()
        response = AttrDict(response)
        print('----- update -----')
        print(response)
        self.assertTrue(response.status)
        self.envOperate_3['env_id'] = None
        response = requests.post(self.envOperate_url, cookies=cookies, json=self.envOperate_3).json()
        response = AttrDict(response)
        print('----- list -----')
        print(response)
        self.assertTrue(response.status)
        response = requests.post(self.envOperate_url, cookies=cookies, json=self.envOperate_4).json()
        response = AttrDict(response)
        print('----- del -----')
        print(response)
        self.assertTrue(response.status)

    def test_operate_api_success(self):
        requests.post(self.register_url, json=self.reg_data)
        response = requests.post(self.login_url, json=self.login_data).json()
        response = AttrDict(response)
        cookies = {'token': response.data.token}
        payload = {
            'project_name': 'app',
            'owner_name': '003'
        }
        response = requests.post(self.add_project_url, cookies=cookies, json=payload).json()
        response = AttrDict(response)
        project_id = response.data.project_id
        self.moduleOperate_1['project_id'] = project_id
        response = requests.post(self.moduleOperate_url, cookies=cookies, json=self.moduleOperate_1).json()
        response = AttrDict(response)
        module_id = response.data.module_id

        self.apiOperate_1['project_id'] = project_id
        self.apiOperate_1['module_id'] = module_id
        response = requests.post(self.apiOperate_url, cookies=cookies, json=self.apiOperate_1).json()
        response = AttrDict(response)
        print('----- add -----')
        print(response)
        self.assertTrue(response.status)

        api_id = response.data.api_id
        self.apiOperate_2['project_id'] = project_id
        self.apiOperate_2['module_id'] = module_id
        self.apiOperate_2['api_id'] = api_id
        response = requests.post(self.apiOperate_url, cookies=cookies, json=self.apiOperate_2).json()
        response = AttrDict(response)
        print('----- update -----')
        print(response)
        self.assertTrue(response.status)

        self.apiOperate_1['operate_type'] = '3'
        self.apiOperate_1['api_id'] = None
        self.apiOperate_1['module_id'] = None
        self.apiOperate_1['project_id'] = None
        response = requests.post(self.apiOperate_url, cookies=cookies, json=self.apiOperate_1).json()
        response = AttrDict(response)
        print('----- list -----')
        print(response)
        self.assertTrue(response.status)

        self.apiOperate_1['operate_type'] = '3'
        self.apiOperate_1['api_id'] = api_id
        response = requests.post(self.apiOperate_url, cookies=cookies, json=self.apiOperate_1).json()
        response = AttrDict(response)
        print('----- found -----')
        print(response)
        self.assertTrue(response.status)

        self.apiOperate_1['operate_type'] = '3'
        self.apiOperate_1['api_id'] = None
        self.apiOperate_1['module_id'] = module_id
        response = requests.post(self.apiOperate_url, cookies=cookies, json=self.apiOperate_1).json()
        response = AttrDict(response)
        print('----- list module api -----')
        print(response)
        self.assertTrue(response.status)

        self.apiOperate_1['operate_type'] = '3'
        self.apiOperate_1['api_id'] = None
        self.apiOperate_1['project_id'] = project_id
        self.apiOperate_1['module_id'] = None
        response = requests.post(self.apiOperate_url, cookies=cookies, json=self.apiOperate_1).json()
        response = AttrDict(response)
        print('----- list project-module api -----')
        print(response)
        self.assertTrue(response.status)

        self.apiOperate_2['operate_type'] = '4'
        self.apiOperate_2['api_id'] = [api_id]
        response = requests.post(self.apiOperate_url, cookies=cookies, json=self.apiOperate_2).json()
        response = AttrDict(response)
        print('----- del -----')
        print(response)
        self.assertTrue(response.status)

        response = requests.post(self.apiOperate_url, cookies=cookies, json=self.apiOperate_11).json()
        response = AttrDict(response)
        print('----- Run -----')
        print(response)
        self.assertTrue(response.data.success)

    def test_operate_testcase_success(self):
        requests.post(self.register_url, json=self.reg_data)
        response = requests.post(self.login_url, json=self.login_data).json()
        response = AttrDict(response)
        cookies = {'token': response.data.token}
        payload = {
            'project_name': 'app',
            'owner_name': '003'
        }
        response = requests.post(self.add_project_url, cookies=cookies, json=payload).json()
        response = AttrDict(response)

        project_id = response.data.project_id
        self.moduleOperate_1['project_id'] = project_id
        response = requests.post(self.moduleOperate_url, cookies=cookies, json=self.moduleOperate_1).json()
        response = AttrDict(response)
        module_id = response.data.module_id

        self.apiOperate_5['project_id'] = project_id
        self.apiOperate_5['module_id'] = module_id
        self.apiOperate_5['operate_type'] = '1'
        response = requests.post(self.apiOperate_url, cookies=cookies, json=self.apiOperate_5).json()
        response = AttrDict(response)
        self.assertTrue(response.status)
        api_id1 = response.data.api_id

        self.apiOperate_6['project_id'] = project_id
        self.apiOperate_6['module_id'] = module_id
        self.apiOperate_6['operate_type'] = '1'
        response = requests.post(self.apiOperate_url, cookies=cookies, json=self.apiOperate_6).json()
        response = AttrDict(response)
        self.assertTrue(response.status)
        api_id2 = response.data.api_id

        self.envOperate_1_1['project_id'] = project_id
        response = requests.post(self.envOperate_url, cookies=cookies, json=self.envOperate_1_1).json()
        response = AttrDict(response)
        env_id1 = response.data.env_id

        self.envOperate_1_2['project_id'] = project_id
        response = requests.post(self.envOperate_url, cookies=cookies, json=self.envOperate_1_2).json()
        response = AttrDict(response)
        env_id2 = response.data.env_id

        self.teststepOperate_1['api_id'] = api_id1
        self.teststepOperate_1['env_id'] = env_id1
        self.teststepOperate_1['teststep_id'] = ''

        response = requests.post(self.testStepOperate_url, cookies=cookies, json=self.teststepOperate_1).json()
        response = AttrDict(response)
        print('----- add -step1----')
        print(self.teststepOperate_1)
        print(response)
        self.assertTrue(response.status)
        step_id1 = response.data.teststep_id
        step_name1 = response.data.teststep_name

        self.teststepOperate_2['api_id'] = api_id2
        self.teststepOperate_2['env_id'] = env_id2
        self.teststepOperate_2['teststep_id'] = ''

        response = requests.post(self.testStepOperate_url, cookies=cookies, json=self.teststepOperate_2).json()
        response = AttrDict(response)
        print('----- add -step2----')
        print(response)
        self.assertTrue(response.status)
        step_id2 = response.data.teststep_id
        step_name2 = response.data.teststep_name

        self.testcaseOperate_1['project_id'] = project_id
        self.testcaseOperate_1['api_id'] = api_id1
        self.testcaseOperate_1['env_id'] = env_id1
        self.testcaseOperate_1['testcase_id'] = ''
        self.testcaseOperate_1['teststeps'] = '[{"step_id": %d, "step_name": "%s"},{"step_id": %d, "step_name": "%s"}]' \
                                              % (step_id1, step_name1, step_id2, step_name2)
        self.testcaseOperate_1['operate_type'] = '4'

        print('----- run -----')
        response = requests.post(self.testCaseOperate_url, cookies=cookies, json=self.testcaseOperate_1).json()
        response = AttrDict(response)
        print('input: %s' % self.testcaseOperate_1)
        print('output: %s' % response)
        self.assertTrue(response.data.success)

        self.testcaseOperate_1['operate_type'] = '1'

        response = requests.post(self.testCaseOperate_url, cookies=cookies, json=self.testcaseOperate_1).json()
        response = AttrDict(response)
        print('----- add -----')
        print('input: %s' % self.testcaseOperate_1)
        print('output: %s' % response)
        self.assertTrue(response.status)

        testcase_id = response.data.testcase_id

        self.testcaseOperate_1['testcase_id'] = testcase_id
        self.testcaseOperate_1['name'] = 'test_2'

        response = requests.post(self.testCaseOperate_url, cookies=cookies, json=self.testcaseOperate_1).json()
        response = AttrDict(response)
        print('----- update -----')
        print('input: %s' % self.testcaseOperate_1)
        print('output: %s' % response)
        self.assertTrue(response.status)

        self.testcaseOperate_1['operate_type'] = '2'

        response = requests.post(self.testCaseOperate_url, cookies=cookies, json=self.testcaseOperate_1).json()
        response = AttrDict(response)
        print('----- find -----')
        print('input: %s' % self.testcaseOperate_1)
        print('output: %s' % response)
        self.assertTrue(response.status)

        self.testcaseOperate_1['operate_type'] = '3'
        self.testcaseOperate_1['testcase_id'] = [testcase_id]

        response = requests.post(self.testCaseOperate_url, cookies=cookies, json=self.testcaseOperate_1).json()
        response = AttrDict(response)
        print('----- delete -----')
        print('input: %s' % self.testcaseOperate_1)
        print('output: %s' % response)
        self.assertTrue(response.status)

        self.testcaseOperate_1['testcase_id'] = None
        self.testcaseOperate_1['name'] = 'test_3'
        self.testcaseOperate_1['operate_type'] = '1'

        response = requests.post(self.testCaseOperate_url, cookies=cookies, json=self.testcaseOperate_1).json()
        response = AttrDict(response)
        print('----- add -----')
        print('input: %s' % self.testcaseOperate_1)
        print('output: %s' % response)
        self.assertTrue(response.status)

        self.testcaseOperate_1['operate_type'] = '2'
        self.testcaseOperate_1['project_id'] = None
        self.testcaseOperate_1['module_id'] = None

        response = requests.post(self.testCaseOperate_url, cookies=cookies, json=self.testcaseOperate_1).json()
        response = AttrDict(response)
        print('----- list -----')
        print('input: %s' % self.testcaseOperate_1)
        print('output: %s' % response)
        self.assertTrue(response.status)

        self.testcaseOperate_1['operate_type'] = '2'
        self.testcaseOperate_1['project_id'] = project_id
        response = requests.post(self.testCaseOperate_url, cookies=cookies, json=self.testcaseOperate_1).json()
        response = AttrDict(response)
        print('----- list project case -----')
        print('input: %s' % self.testcaseOperate_1)
        print('output: %s' % response)
        self.assertTrue(response.status)

        self.testcaseOperate_1['operate_type'] = '2'
        self.testcaseOperate_1['module_id'] = module_id
        response = requests.post(self.testCaseOperate_url, cookies=cookies, json=self.testcaseOperate_1).json()
        response = AttrDict(response)
        print('----- list module case -----')
        print('input: %s' % self.testcaseOperate_1)
        print('output: %s' % response)
        self.assertTrue(response.status)

    def test_operate_testcase_batch_success(self):
        requests.post(self.register_url, json=self.reg_data)
        response = requests.post(self.login_url, json=self.login_data).json()
        response = AttrDict(response)
        cookies = {'token': response.data.token}
        payload = {
            'project_name': 'app',
            'owner_name': '003'
        }
        response = requests.post(self.add_project_url, cookies=cookies, json=payload).json()
        response = AttrDict(response)

        project_id = response.data.project_id

        response = requests.post(self.moduleOperate_url, cookies=cookies, json=self.moduleOperate_1).json()
        response = AttrDict(response)
        module_id = response.data.module_id

        self.apiOperate_7['project_id'] = project_id
        self.apiOperate_7['module_id'] = module_id
        self.apiOperate_7['operate_type'] = '1'

        response = requests.post(self.apiOperate_url, cookies=cookies, json=self.apiOperate_7).json()
        response = AttrDict(response)
        self.assertTrue(response.status)
        api_id3 = response.data.api_id

        self.envOperate_1_3['project_id'] = project_id
        response = requests.post(self.envOperate_url, cookies=cookies, json=self.envOperate_1_3).json()
        response = AttrDict(response)
        env_id3 = response.data.env_id

        self.teststepOperate_3['api_id'] = api_id3
        self.teststepOperate_3['env_id'] = env_id3
        self.teststepOperate_3['teststep_id'] = ''
        response = requests.post(self.testStepOperate_url, cookies=cookies, json=self.teststepOperate_3).json()
        response = AttrDict(response)
        print('----- add step3----')
        print(response)
        self.assertTrue(response.status)
        step_id3 = response.data.teststep_id
        step_name3 = response.data.teststep_name

        self.testcaseOperate_1['project_id'] = project_id
        self.testcaseOperate_1['api_id'] = api_id3
        self.testcaseOperate_1['env_id'] = ''
        self.testcaseOperate_1['testcase_id'] = ''
        self.testcaseOperate_1['teststeps'] = '[{"step_id": %d, "step_name": "%s"}]' % (step_id3, step_name3)
        self.testcaseOperate_1['operate_type'] = '1'
        self.testcaseOperate_1['name'] = 'getinfo'
        response = requests.post(self.testCaseOperate_url, cookies=cookies, json=self.testcaseOperate_1).json()
        response = AttrDict(response)
        print('----- add 2-----')
        print(response)
        self.assertTrue(response.status)
        testcase_id2 = response.data.testcase_id

        self.apiOperate_5['project_id'] = project_id
        self.apiOperate_5['module_id'] = module_id
        self.apiOperate_5['operate_type'] = '1'
        response = requests.post(self.apiOperate_url, cookies=cookies, json=self.apiOperate_5).json()
        response = AttrDict(response)
        self.assertTrue(response.status)
        api_id1 = response.data.api_id

        self.apiOperate_6['project_id'] = project_id
        self.apiOperate_6['module_id'] = module_id
        self.apiOperate_6['operate_type'] = '1'
        response = requests.post(self.apiOperate_url, cookies=cookies, json=self.apiOperate_6).json()
        response = AttrDict(response)
        self.assertTrue(response.status)
        api_id2 = response.data.api_id

        self.envOperate_1_1['project_id'] = project_id
        response = requests.post(self.envOperate_url, cookies=cookies, json=self.envOperate_1_1).json()
        response = AttrDict(response)
        env_id1 = response.data.env_id

        self.envOperate_1_2['project_id'] = project_id
        response = requests.post(self.envOperate_url, cookies=cookies, json=self.envOperate_1_2).json()
        response = AttrDict(response)
        env_id2 = response.data.env_id

        self.teststepOperate_1['api_id'] = api_id1
        self.teststepOperate_1['env_id'] = env_id1
        self.teststepOperate_1['teststep_id'] = ''

        response = requests.post(self.testStepOperate_url, cookies=cookies, json=self.teststepOperate_1).json()
        response = AttrDict(response)
        print('----- add -step1----')
        print(response)
        self.assertTrue(response.status)
        step_id1 = response.data.teststep_id
        step_name1 = response.data.teststep_name

        self.teststepOperate_2['api_id'] = api_id2
        self.teststepOperate_2['env_id'] = env_id2
        self.teststepOperate_2['teststep_id'] = ''

        response = requests.post(self.testStepOperate_url, cookies=cookies, json=self.teststepOperate_2).json()
        response = AttrDict(response)
        print('----- add -step2----')
        print(response)
        self.assertTrue(response.status)
        step_id2 = response.data.teststep_id
        step_name2 = response.data.teststep_name

        self.testcaseOperate_1['project_id'] = project_id
        self.testcaseOperate_1['api_id'] = api_id1
        self.testcaseOperate_1['env_id'] = env_id1
        self.testcaseOperate_1['testcase_id'] = ''
        self.testcaseOperate_1['teststeps'] = '[{"step_id": %d, "step_name": "%s"},{"step_id": %d, "step_name": "%s"}]' \
                                              % (step_id1, step_name1, step_id2, step_name2)
        self.testcaseOperate_1['operate_type'] = '1'
        self.testcaseOperate_1['name'] = 'case2'
        response = requests.post(self.testCaseOperate_url, cookies=cookies, json=self.testcaseOperate_1).json()
        response = AttrDict(response)
        print('----- add -----')
        print(response)
        self.assertTrue(response.status)
        testcase_id1 = response.data.testcase_id

        self.testsBatchRun_1['project_id'] = project_id
        self.testsBatchRun_1['test_id_items'] = [testcase_id2, testcase_id1]

        response = requests.post(self.testsBatchRun_url, cookies=cookies, json=self.testsBatchRun_1).json()
        response = AttrDict(response)
        print('----- batch run-----')
        print(self.testsBatchRun_1)
        print(response)
        self.assertTrue(response.status)
        report_id_items = response.data.report_id_items

        self.report_1['testcase_id'] = testcase_id2
        self.report_1['report_id'] = None
        response = requests.post(self.report_url, cookies=cookies, json=self.report_1).json()
        response = AttrDict(response)
        print('----- report list-----')
        print(self.report_1)
        print(response)
        self.assertTrue(response.status)

        self.report_1['testcase_id'] = testcase_id2
        self.report_1['report_id'] = report_id_items[0]
        response = requests.post(self.report_url, cookies=cookies, json=self.report_1).json()
        response = AttrDict(response)
        print('----- found-----')
        print(self.report_1)
        print(response)
        self.assertTrue(response.status)

        self.report_1['report_id'] = report_id_items
        self.report_1['operate_type'] = '3'
        response = requests.post(self.report_url, cookies=cookies, json=self.report_1).json()
        response = AttrDict(response)
        print('----- del -----')
        print(self.report_1)
        print(response)
        self.assertTrue(response.status)

    def test_operate_teststep_success(self):
        requests.post(self.register_url, json=self.reg_data)
        response = requests.post(self.login_url, json=self.login_data).json()
        response = AttrDict(response)
        cookies = {'token': response.data.token}
        payload = {
            'project_name': 'app',
            'owner_name': '003'
        }
        response = requests.post(self.add_project_url, cookies=cookies, json=payload).json()
        response = AttrDict(response)

        project_id = response.data.project_id

        response = requests.post(self.moduleOperate_url, cookies=cookies, json=self.moduleOperate_1).json()
        response = AttrDict(response)
        module_id = response.data.module_id
        self.apiOperate_1['project_id'] = project_id
        self.apiOperate_1['module_id'] = module_id
        response = requests.post(self.apiOperate_url, cookies=cookies, json=self.apiOperate_1).json()
        response = AttrDict(response)
        self.assertTrue(response.status)

        api_id = response.data.api_id

        self.envOperate_1_1['project_id'] = project_id
        response = requests.post(self.envOperate_url, cookies=cookies, json=self.envOperate_1_1).json()
        response = AttrDict(response)

        env_id = response.data.env_id

        self.teststepOperate_1['api_id'] = api_id
        self.teststepOperate_1['env_id'] = env_id
        self.teststepOperate_1['teststep_id'] = ''

        response = requests.post(self.testStepOperate_url, cookies=cookies, json=self.teststepOperate_1).json()
        response = AttrDict(response)
        print('----- add -----')
        print(self.teststepOperate_1)
        print(response)
        self.assertTrue(response.status)

        teststep_id = response.data.teststep_id
        self.teststepOperate_1['teststep_id'] = teststep_id
        self.teststepOperate_1['name'] = 'teststep_2'

        response = requests.post(self.testStepOperate_url, cookies=cookies, json=self.teststepOperate_1).json()
        response = AttrDict(response)
        print('----- update -----')
        print(response)
        print(self.teststepOperate_1)
        self.assertTrue(response.status)

        self.teststepOperate_1['operate_type'] = '2'

        response = requests.post(self.testStepOperate_url, cookies=cookies, json=self.teststepOperate_1).json()
        response = AttrDict(response)
        print('----- find -----')
        print(self.teststepOperate_1)
        print(response)
        self.assertTrue(response.status)

        self.teststepOperate_1['operate_type'] = '3'

        response = requests.post(self.testStepOperate_url, cookies=cookies, json=self.teststepOperate_1).json()
        response = AttrDict(response)
        print('----- delete -----')
        print(self.teststepOperate_1)
        print(response)
        self.assertTrue(response.status)


if __name__ == '__main__':
    unittest.main(verbosity=2)
