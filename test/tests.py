from datetime import datetime, timedelta
import unittest
import requests
from app import create_app, db
from app.models import User, Project
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
        host = 'http://127.0.0.1:5000'
        self.register_url = host + '/auth/register'
        self.login_url = host + '/auth/login'
        self.logout_url = host + '/auth/logout'
        self.get_projects_url = host + '/api/projectsList'
        self.add_project_url = host + '/api/projectCreate'
        self.project_has_user_url = host + '/api/project_has_user'
        self.get_project_url = host + '/api/projectInfo'
        self.del_project_url = host + '/api/projectDel'
        self.update_project_url = host + '/api/projectUpdate'

    def tearDown(self):
        db.session.remove()
        user1 = User.query.filter_by(username='003').first()
        user2 = User.query.filter_by(username='007').first()
        project = Project.query.filter_by(project_name='app').first()
        # try:
        if user1:
            db.session.delete(user1)
        if user2:
            db.session.delete(user2)
        if project:
            db.session.delete(project)
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
        payload = {'pageNum': '1', 'perPage': '20'}
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
            'username_list': ['007']
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
            'username_list': ['007']
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
            'username_list': ['006']
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
            'username_list': ['007']
        }
        requests.post(self.project_has_user_url, cookies=cookies, json=payload)
        payload = {
            'project_name': 'app',
            'username_list': ['007']
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
            'username_list': ['003']
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








    #     u1.unfollow(u2)
    #     db.session.commit()
    #     self.assertFalse(u1.is_following(u2))
    #     self.assertEqual(u1.followed.count(), 0)
    #     self.assertEqual(u2.followers.count(), 0)
    #
    # def test_follow_posts(self):
    #     # create four users
    #     u1 = User(username='john', email='john@example.com')
    #     u2 = User(username='susan', email='susan@example.com')
    #     u3 = User(username='mary', email='mary@example.com')
    #     u4 = User(username='david', email='david@example.com')
    #     db.session.add_all([u1, u2, u3, u4])
    #
    #     # create four posts
    #     now = datetime.utcnow()
    #     p1 = Post(body="post from john", author=u1,
    #               timestamp=now + timedelta(seconds=1))
    #     p2 = Post(body="post from susan", author=u2,
    #               timestamp=now + timedelta(seconds=4))
    #     p3 = Post(body="post from mary", author=u3,
    #               timestamp=now + timedelta(seconds=3))
    #     p4 = Post(body="post from david", author=u4,
    #               timestamp=now + timedelta(seconds=2))
    #     db.session.add_all([p1, p2, p3, p4])
    #     db.session.commit()
    #
    #     # setup the followers
    #     u1.follow(u2)  # john follows susan
    #     u1.follow(u4)  # john follows david
    #     u2.follow(u3)  # susan follows mary
    #     u3.follow(u4)  # mary follows david
    #     db.session.commit()
    #
    #     # check the followed posts of each user
    #     f1 = u1.followed_posts().all()
    #     f2 = u2.followed_posts().all()
    #     f3 = u3.followed_posts().all()
    #     f4 = u4.followed_posts().all()
    #     self.assertEqual(f1, [p2, p4, p1])
    #     self.assertEqual(f2, [p2, p3])
    #     self.assertEqual(f3, [p3, p4])
    #     self.assertEqual(f4, [p4])


if __name__ == '__main__':
    unittest.main(verbosity=2)
