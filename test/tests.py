from datetime import datetime, timedelta
import unittest
import requests
from app import create_app, db
from app.models import User, Project, Module
from config import Config
from app.common import AttrDict


class TestRegLoginCase(unittest.TestCase):

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
            'project_name': 'app',
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
        host = 'http://127.0.0.1:5000'
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

    def tearDown(self):
        db.session.remove()
        user1 = User.query.filter_by(username='003').first()
        user2 = User.query.filter_by(username='007').first()
        project1 = Project.query.filter_by(project_name='app').first()
        project2 = Project.query.filter_by(project_name='cpp').first()
        module1 = Module.query.filter_by(module_name='app_module_1').first()
        module2 = Module.query.filter_by(module_name='app_module_2').first()
        module3 = Module.query.filter_by(module_name='aa').first()
        module4 = Module.query.filter_by(module_name='bb').first()
        # try:
        if user1:
            db.session.delete(user1)
        if user2:
            db.session.delete(user2)
        if project1:
            db.session.delete(project1)
        if project2:
            db.session.delete(project2)
        if module1:
            db.session.delete(module1)
        if module2:
            db.session.delete(module2)
        if module3:
            db.session.delete(module3)
        if module4:
            db.session.delete(module4)

        db.session.commit()
        # except Exception as error:
        #     print(error)

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
        requests.post(self.add_project_url, cookies=cookies, json=payload)
        requests.post(self.register_url, json=self.reg_data_copy)
        payload = {
            'project_name': 'app',
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
        requests.post(self.add_project_url, cookies=cookies, json=payload)
        payload = {'project_name': 'app'}
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
        requests.post(self.add_project_url, cookies=cookies, json=payload)
        payload = {
            'project_name': 'cpp',
            'owner_name': '007',
            'origin_project_name': 'app',
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
        payload = {'page_num': '1', 'per_page': '20'}
        response = requests.get(self.get_users_url, cookies=cookies, params=payload).json()
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

        # response = AttrDict(response)
        # print(response)
        # self.assertTrue(response.status)

    def test_get_modules_success(self):
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


if __name__ == '__main__':
    unittest.main(verbosity=2)
