import base64
import os
import json
import ast
from app import db
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask import g
from app.common import list_to_obj, list_to_obj_2, data_to_server, to_front, dict_to_obj


# class FromAPIMixin(object):
#     @staticmethod
#     def from_dict(attr, data):
#         for field in attr:
#             if field in data:
#                 setattr(field, data[field])


project_user = db.Table('project_user',
                        db.Column('project_id', db.Integer, db.ForeignKey('project.id')),
                        db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
                        )


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), index=True, unique=True)
    email = db.Column(db.String(255), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    is_administrator = db.Column(db.Boolean, default=False)
    token = db.Column(db.String(32), index=True, unique=True)
    token_expiration = db.Column(db.DateTime)
    teststeps = db.relationship('TestStep', backref='user', lazy='dynamic')
    # create_projects = db.relationship('Project', backref='owner', lazy='dynamic')

    # projects = db.relationship(
    #     'Project', secondary=user_project,
    #     backref=db.backref('users', lazy='dynamic'), lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def admins_list():
        admins = User.query.filter_by(is_administrator=True).all()
        return admins

    def add(self):
        db.session.add(self)

    def to_dict(self):
        data = {
            'user_id': self.id,
            'username': self.username,
            'is_administrator': self.is_administrator,
            'project_list': [project.project_name for project in self.followed_projects().all()]
        }
        return data

    def from_dict(self, data):
        for field in ['username', 'email']:
            if field in data:
                setattr(self, field, data[field])
        if 'password' in data:
            self.set_password(data['password'])

    def get_token(self, expires_in=3600):
        now = datetime.utcnow()
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token
        self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        return self.token

    def revoke_token(self):
        self.token_expiration = datetime.utcnow() - timedelta(seconds=1)

    @staticmethod
    def check_token(token):
        user = User.query.filter_by(token=token).first()
        if user is None or user.token_expiration < datetime.utcnow():
            return None
        return user

    def followed_projects(self):
        followed = self.projects
        own = Project.query.filter_by(owner_name=self.username)
        return followed.union(own).order_by(Project.timestamp.desc())

    @staticmethod
    def to_collection_dict():
        # users = User.query.paginate(page_num, per_page, False)
        users = User.query.all()
        data = {
            'users': [user.to_dict() for user in users]
        }
        # data = {
        #     'users': [user.to_dict() for user in users.items],
        #     'meta': {
        #         'has_next': users.has_next,
        #         'next_num': users.next_num,
        #         'has_prev': users.has_prev,
        #         'prev_num': users.prev_num
        #     }
        # }
        return data


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_name = db.Column(db.String(255), index=True, unique=True, nullable=False)
    owner_name = db.Column(db.String(255), index=True, nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    modules = db.relationship('Module', backref='project', lazy='dynamic')
    envs = db.relationship('Env', backref='project', lazy='dynamic')
    apis = db.relationship('Api', backref='project', lazy='dynamic')
    testcases = db.relationship('TestCase', backref='project', lazy='dynamic')
    teststeps = db.relationship('TestStep', backref='project', lazy='dynamic')
    suites = db.relationship('Suite', backref='project', lazy='dynamic')
    users = db.relationship(
        'User', secondary=project_user,
        backref=db.backref('projects', lazy='dynamic'), lazy='dynamic')

    def __repr__(self):
        return '<Project {}>'.format(self.project_name)

    def from_dict(self, data):
        for field in ['project_name', 'owner_name']:
            if field in data:
                setattr(self, field, data[field])

    def to_dict(self):
        module_list = []
        for module in self.modules.order_by(Module.timestamp.desc()).all():
            api_list = []
            for api in module.apis.order_by(Api.timestamp.desc()).all():
                api_dict = {'name': api.name, 'id': api.id, 'url': api.req_relate_url, 'method': api.req_method}
                api_list.append(api_dict)
            module_dict = {'name': module.module_name, 'id': module.id, 'api_list': api_list}
            module_list.append(module_dict)

        env_list = []
        for env in self.envs.order_by(Env.timestamp.desc()).all():
            env_obj = {
                'env_id': env.id,
                'env_name': env.env_name,
                'env_desc': env.env_desc,
                'env_host': env.env_host
            }
            env_list.append(env_obj)

        suite_list = []
        for suite in self.suites.order_by(Suite.timestamp.desc()).all():
            suite_obj = {
                'suite_id': suite.id,
                'suite_name': suite.suite_name
            }
            suite_list.append(suite_obj)

        api_list = []
        for api in self.apis.order_by(Api.timestamp.desc()).all():
            api_obj = {
                'api_id': api.id,
                'api_name': api.name
            }
            api_list.append(api_obj)

        data = {
            'project_id': self.id,
            'project_name': self.project_name,
            'project_owner': self.owner_name,
            'timestamp': self.timestamp,
            'modules': {
                'count': self.modules.count(),
                'list': module_list
            },
            'suites': {
                'count': self.suites.count(),
                'list': suite_list
            },
            'testcases_count': self.testcases.count(),
            'apis': {
                'count': self.apis.count(),
                'list': api_list
            },
            'envs': {
                'count': self.envs.count(),
                'list': env_list
            },
            'users': {
                'count': self.users.count(),
                'list': [int(user.id) for user in self.users.order_by(User.id).all()]
            }
        }
        return data

    def follow(self, user):
        if not self.is_following(user):
            self.users.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.users.remove(user)

    def is_following(self, user):
        return user in self.users.all()

    @staticmethod
    def to_collection_dict(page_num, per_page):
        projects = g.current_user.followed_projects().paginate(page_num, per_page, False)
        data = {
            'project_items': [project.to_dict() for project in projects.items],
            'meta': {
                'has_next': projects.has_next,
                'next_num': projects.next_num,
                'has_prev': projects.has_prev,
                'prev_num': projects.prev_num
            }
        }
        return data

    def to_collection_suite_dict(self):
        suites_data = []
        for suite in self.suites.order_by(Suite.timestamp.desc()).all():
            tests_data = []
            for test in suite.testcases.order_by(TestCase.timestamp.desc()).all():
                teststeps_data = []
                for item in json.loads(test.teststeps):
                    step_id = item['step_id']
                    teststep = TestStep.query.get_or_404(step_id)
                    api = Api.query.get_or_404(teststep.api_id)
                    step_data = {
                        'step_id': step_id,
                        'step_name': teststep.name,
                        'api': api.req_relate_url
                    }
                    teststeps_data.append(step_data)
                test_api_count = len(json.loads(test.teststeps))
                reports_data = [report.to_dict() for report in test.reports.all()]
                test_data = {
                    'test_id': test.id,
                    'test_name': test.name,
                    'test_api_count': test_api_count,
                    'teststeps_data': teststeps_data,
                    'reports_data': reports_data
                }
                tests_data.append(test_data)
            suite_data = {
                'suite_id': suite.id,
                'suite_name': suite.suite_name,
                'tests_data': tests_data
            }
            suites_data.append(suite_data)

        payload = {
            'project_id': self.id,
            'project_name': self.project_name,
            'suites_data': suites_data
        }
        return payload

    def to_collection_step_dict(self):
        teststeps_data = []
        for module in self.modules.order_by(Module.timestamp.desc()).all():
            for api in module.apis.order_by(Api.timestamp.desc()).all():
                for step in api.teststeps.order_by(TestStep.timestamp.desc()).all():
                    api_obj = Api.query.get_or_404(step.api_id)
                    env_obj = Env.query.get_or_404(step.env_id)
                    user_obj = User.query.get_or_404(step.user_id)
                    report_obj = step.reports.order_by(Report.timestamp.desc()).first()
                    api_data = {'api_id': api_obj.id, 'api_name': api_obj.name, 'api_url': api_obj.req_relate_url}
                    env_data = {'env_id': env_obj.id, 'env_name': env_obj.env_name}
                    user_data = {'user_id': user_obj.id, 'user_name': user_obj.username}
                    report_data = {
                        'report_id': report_obj.id if report_obj else '',
                        'report_result': str(report_obj.test_result) if report_obj else '',
                        'report_time': report_obj.timestamp.strftime('%Y/%m/%d %H:%M:%S') if report_obj else ''
                    }

                    step_data = {
                        'step_id': step.id,
                        'step_name': step.name,
                        'api': api_data,
                        'env': env_data,
                        'user': user_data,
                        'report': report_data
                    }
                    teststeps_data.append(step_data)

        payload = {
            'project': {'project_id': self.id, 'project_name': self.project_name},
            'teststeps': teststeps_data
        }
        return payload


class Module(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    module_name = db.Column(db.String(255), index=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    apis = db.relationship('Api', backref='module', lazy='dynamic')

    def __repr__(self):
        return '<Module {}>'.format(self.module_name)

    def from_dict(self, data):
        for field in ['module_name', 'project_id']:
            if field in data:
                setattr(self, field, data[field])

    def to_dict(self):
        api_list = []
        for api in self.apis.order_by(Api.timestamp.desc()).all():
            api_dict = {'name': api.name, 'id': api.id, 'url': api.req_relate_url, 'method': api.req_method}
            api_list.append(api_dict)
        data = {
            'module_id': self.id,
            'module_name': self.module_name,
            'project_id': self.project_id,
            'timestamp': self.timestamp,
            'apis': {
                'count': self.apis.count(),
                'list': api_list
            }
        }
        return data

    def to_collection_step_dict(self):
        project = Project.query.get_or_404(self.project_id)

        teststeps_data = []
        for api in self.apis.order_by(Api.timestamp.desc()).all():
            for step in api.teststeps.order_by(TestStep.timestamp.desc()).all():

                api = Api.query.get_or_404(step.api_id)
                env = Env.query.get_or_404(step.env_id)
                user = User.query.get_or_404(step.user_id)
                report_obj = step.reports.order_by(Report.timestamp.desc()).first()
                report_data = {
                    'report_id': report_obj.id if report_obj else '',
                    'report_result': str(report_obj.test_result) if report_obj else '',
                    'report_time': report_obj.timestamp.strftime('%Y/%m/%d %H:%M:%S') if report_obj else ''
                }

                step_data = {
                    'step_id': step.id,
                    'step_name': step.name,
                    'api': {'api_id': api.id, 'api_name': api.name, 'api_url': api.req_relate_url},
                    'env': {'env_id': env.id, 'env_name': env.env_name},
                    'user': {'user_id': user.id, 'user_name': user.username},
                    'report': report_data
                }
                teststeps_data.append(step_data)

        payload = {
            'project': {'project_id': project.id, 'project_name': project.project_name},
            'teststeps': teststeps_data
        }
        return payload


class Env(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    env_name = db.Column(db.String(255), index=True)
    env_desc = db.Column(db.Text())
    env_host = db.Column(db.String(255))
    env_var = db.Column(db.Text())
    extracts = db.Column(db.Text())
    asserts = db.Column(db.Text())
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    testcases = db.relationship('TestCase', backref='env', lazy='dynamic')
    teststeps = db.relationship('TestStep', backref='env', lazy='dynamic')

    def __repr__(self):
        return '<Env {}>'.format(self.env_name)

    def from_dict(self, data):
        for field in ['env_name', 'env_desc', 'env_host']:
            if field in data:
                setattr(self, field, data[field])

        for field in ['env_var', 'extracts']:
            if field in data:
                payload = []
                for obj in data[field]:
                    obj_t = {obj['key']: obj['value']}
                    payload.append(obj_t)

                payload_tostr = json.dumps(payload)
                setattr(self, field, payload_tostr)

        if 'asserts' in data:
            payload = []
            for obj in data['asserts']:
                obj_t = {obj['eq']: [obj['actual'], obj['expect']]}
                payload.append(obj_t)

            payload_tostr = json.dumps(payload)
            setattr(self, 'asserts', payload_tostr)

        if data['project_id']:
            self.project_id = data['project_id']

    def to_dict(self):

        env_var = list_to_obj(self.env_var)
        extracts = list_to_obj(self.extracts)
        asserts = list_to_obj_2(self.asserts)

        data = {
            'env_id': self.id,
            'env_name': self.env_name,
            'project_id': self.project_id,
            'env_desc': self.env_desc,
            'env_host': self.env_host,
            'env_var': env_var,
            'extracts': extracts,
            'asserts': asserts,
            'timestamp': self.timestamp,
            'testcases': {
                'count': self.testcases.count(),
                'list': [testcase.id for testcase in self.testcases.order_by(TestCase.timestamp.desc()).all()]
            },
            'teststeps': {
                'count': self.teststeps.count(),
                'list': [teststep.id for teststep in self.teststeps.order_by(TestStep.timestamp.desc()).all()]
            }
        }
        return data

    @staticmethod
    def to_collection_dict(page_num, per_page):
        projects = g.current_user.followed_projects().paginate(page_num, per_page, False)
        project_list = projects.items
        payload = []
        for project in project_list:
            env_list = []
            for env in project.envs.all():
                env_data = env.to_dict()
                env_list.append(env_data)
            project_data = {
                'project_name': project.project_name,
                'env_list': env_list
            }
            payload.append(project_data)

        data = {
            'env_items': payload,
            'meta': {
                'has_next': projects.has_next,
                'next_num': projects.next_num,
                'has_prev': projects.has_prev,
                'prev_num': projects.prev_num
            }
        }
        return data


class Api(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    req_method = db.Column(db.String(255))
    req_temp_host = db.Column(db.String(255))
    req_relate_url = db.Column(db.String(255))
    req_headers = db.Column(db.Text())
    req_cookies = db.Column(db.Text())
    req_params = db.Column(db.Text())
    req_data_type = db.Column(db.String(255))
    req_body = db.Column(db.Text())
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    module_id = db.Column(db.Integer, db.ForeignKey('module.id'))
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    testcases = db.relationship('TestCase', backref='api', lazy='dynamic')
    teststeps = db.relationship('TestStep', backref='api', lazy='dynamic')

    def __repr__(self):
        return '<Api {}>'.format(self.name)

    def from_dict(self, data):
        for field in ['name', 'req_method', 'req_temp_host', 'req_relate_url',
                      'req_headers', 'req_cookies', 'req_params', 'req_data_type', 'req_body']:
            if field in data:
                setattr(self, field, data[field])

        for field in ['req_headers', 'req_cookies', 'req_params', 'req_body']:
            if field in data:
                payload = json.dumps(data_to_server(data.get(field)))
                setattr(self, field, payload)

        if data['module_id']:
            self.module_id = data['module_id']

        if data['project_id']:
            self.project_id = data['project_id']

    def to_dict(self):
        req_headers = dict_to_obj(self.req_headers)
        req_cookies = dict_to_obj(self.req_cookies)
        req_params = dict_to_obj(self.req_params)
        req_body = dict_to_obj(self.req_body)

        testcase_list = []
        for testcase in self.testcases.order_by(TestCase.timestamp.desc()).all():
            testcase_dict = {'name': testcase.name, 'id': testcase.id}
            testcase_list.append(testcase_dict)
        teststep_list = []
        for teststep in self.teststeps.order_by(TestStep.timestamp.desc()).all():
            teststep_dict = {'name': teststep.name, 'id': teststep.id}
            teststep_list.append(teststep_dict)

        data = {
            'api_id': self.id,
            'name': self.name,
            'project_id': self.project_id,
            'module_id': self.module_id,
            'req_method': self.req_method,
            'req_temp_host': self.req_temp_host,
            'req_relate_url': self.req_relate_url,
            'req_headers': req_headers,
            'req_cookies': req_cookies,
            'req_params': req_params,
            'req_data_type': self.req_data_type,
            'req_body': req_body,
            'timestamp': self.timestamp,
            'testcases': {
                'count': self.testcases.count(),
                'list': testcase_list
            },
            'teststeps': {
                'count': self.teststeps.count(),
                'list': teststep_list
            }
        }
        return data

    @staticmethod
    def to_collection_dict(page_num, per_page):
        projects = g.current_user.followed_projects().paginate(page_num, per_page, False)
        project_list = projects.items
        payload = []
        for project in project_list:
            module_list = []
            for module in project.modules.all():
                api_list = []
                for api in module.apis.all():
                    api_data = api.to_dict()
                    api_list.append(api_data)
                module_data = {
                    'module_id': module.id,
                    'module_name': module.module_name,
                    'api_list': api_list
                }
                module_list.append(module_data)
            project_data = {
                'project_id': project.id,
                'project_name': project.project_name,
                'module_list': module_list
            }
            payload.append(project_data)

        data = {
            'Api_items': payload,
            'meta': {
                'has_next': projects.has_next,
                'next_num': projects.next_num,
                'has_prev': projects.has_prev,
                'prev_num': projects.prev_num
            }
        }
        return data

    def to_collection_step_dict(self):
        project = Project.query.get_or_404(self.project_id)

        teststeps_data = []
        for step in self.teststeps.order_by(TestStep.timestamp.desc()).all():

            api = Api.query.get_or_404(step.api_id)
            env = Env.query.get_or_404(step.env_id)
            user = User.query.get_or_404(step.user_id)
            report_obj = step.reports.order_by(Report.timestamp.desc()).first()
            report_data = {
                'report_id': report_obj.id if report_obj else '',
                'report_result': str(report_obj.test_result) if report_obj else '',
                'report_time': report_obj.timestamp.strftime('%Y/%m/%d %H:%M:%S') if report_obj else ''
            }

            step_data = {
                'step_id': step.id,
                'step_name': step.name,
                'api': {'api_id': api.id, 'api_name': api.name, 'api_url': api.req_relate_url},
                'env': {'env_id': env.id, 'env_name': env.env_name},
                'user': {'user_id': user.id, 'user_name': user.username},
                'report': report_data
            }
            teststeps_data.append(step_data)

        payload = {
            'project': {'project_id': project.id, 'project_name': project.project_name},
            'teststeps': teststeps_data
        }
        return payload


class Suite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    suite_name = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    testcases = db.relationship('TestCase', backref='suite', lazy='dynamic')
    # teststeps = db.relationship('TestStep', backref='suite', lazy='dynamic')

    def __repr__(self):
        return '<Suite {}>'.format(self.name)

    def from_dict(self, data):
        for field in ['suite_name', 'project_id']:
            if field in data:
                setattr(self, field, data[field])

    def to_dict(self):
        tests_data = []
        for test in self.testcases.order_by(TestCase.timestamp.desc()).all():
            teststeps_data = []
            for item in json.loads(test.teststeps):
                step_id = item['step_id']
                teststep = TestStep.query.get_or_404(step_id)
                api = Api.query.get_or_404(teststep.api_id)
                step_data = {
                    'step_id': step_id,
                    'step_name': teststep.name,
                    'api': api.req_relate_url
                }
                teststeps_data.append(step_data)
            test_api_count = len(json.loads(test.teststeps))
            reports_data = [report.to_dict() for report in test.reports.all()]
            test_data = {
                'test_id': test.id,
                'test_name': test.name,
                'test_api_count': test_api_count,
                'teststeps_data': teststeps_data,
                'reports_data': reports_data
            }
            tests_data.append(test_data)
        suite_data = {
            'suite_id': self.id,
            'suite_name': self.suite_name,
            'project_id': self.project_id,
            'timestamp': self.timestamp,
            'tests_data': tests_data
        }

        return suite_data

    # @staticmethod
    # def to_collection_dict(page_num, per_page):
    #     projects = g.current_user.followed_projects().paginate(page_num, per_page, False)
    #     project_list = projects.items
    #     payload = []
    #     for project in project_list:
    #         env_list = []
    #         for env in project.envs.all():
    #             env_data = env.to_dict()
    #             env_list.append(env_data)
    #         project_data = {
    #             'project_name': project.project_name,
    #             'env_list': env_list
    #         }
    #         payload.append(project_data)
    #
    #     data = {
    #         'env_items': payload,
    #         'meta': {
    #             'has_next': projects.has_next,
    #             'next_num': projects.next_num,
    #             'has_prev': projects.has_prev,
    #             'prev_num': projects.prev_num
    #         }
    #     }
    #     return data


class TestCase(db.Model):
    __tablename__ = 'testcase'
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    api_id = db.Column(db.Integer, db.ForeignKey('api.id'))
    suite_id = db.Column(db.Integer, db.ForeignKey('suite.id'))
    name = db.Column(db.String(255))
    test_desc = db.Column(db.String(255))
    # {
    #     'teststeps ': [{
    #         'id ': 254,
    #         'name ': '步骤222 '
    #     }, {
    #         'id ': 253,
    #         'name ': '步骤111 '
    #     }]
    # }
    teststeps = db.Column(db.Text())
    # {
    # 'steps': [
    #               [{'key': 'step_id', 'value': 1}, {'key': 'step_seq', 'value': 1}],
    #               [{'key': 'step_id', 'value': 1}, {'key': 'step_seq', 'value': 1}]
    #           ]
    # }
    # "[{'step_id': 1, 'step_name': 'aa'}, {'step_id': 2, 'step_name': 'bb'}]"
    # teststeps = db.relationship('TestStep', backref='testcase', lazy='dynamic')
    env_id = db.Column(db.Integer, db.ForeignKey('env.id'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    reports = db.relationship('Report', backref='testcase', lazy='dynamic')

    def __repr__(self):
        return '<TestCase {}>'.format(self.name)

    def from_dict(self, data):
        for field in ['name', 'test_desc']:
            if field in data:
                setattr(self, field, data[field])

        for field in ['teststeps']:
            if field in data:
                steps = []
                for payload in data.get(field):
                    step = data_to_server(payload)
                    steps.append(step)
                setattr(self, field, steps)

        if data['project_id']:
            self.project_id = data['project_id']

        if data['api_id']:
            self.api_id = data['api_id']

        if data['env_id']:
            self.env_id = data['env_id']

        if data['suite_id']:
            self.suite_id = data['suite_id']

    def to_dict(self):
        api = Api.query.get(self.api_id)
        env = Env.query.get(self.env_id)
        teststeps = to_front(self.teststeps)

        data = {
            'testcase_id': self.id,
            'name': self.name,
            'test_desc': self.test_desc,
            'project_name': Project.query.get(self.project_id).project_name,
            'module_name': Module.query.get(Api.query.get(self.api_id).module_id).module_name,
            'suite_name': Suite.query.get(self.suite_id).suite_name,
            'api_name': api.name,
            'api_url': api.req_relate_url,
            # 'env_id': self.env_id if self.env_id else '',
            'env_name': env.env_name if env else '',
            'env_host': env.env_host if env else '',
            'env_var': env.env_var if env else '',
            'teststeps': teststeps,
            'has_report': True if self.reports.all() else False,
            'timestamp': self.timestamp
        }
        return data

    @staticmethod
    def to_collection_dict(page_num, per_page):
        projects = g.current_user.followed_projects().paginate(page_num, per_page, False)
        project_items = projects.items
        payload = []
        for project in project_items:
            module_items = []
            for module in project.modules.all():
                api_items = []
                for api in module.apis.all():
                    testcases = []
                    for testcase in api.testcases.all():
                        testcase_data = testcase.to_dict()
                        testcases.append(testcase_data)
                    api_data = {
                        'api_id': api.id,
                        'testcases': testcases
                    }
                    api_items.append(api_data)
                module_data = {
                    'module_id': module.id,
                    'api_items': api_items
                }
                module_items.append(module_data)
            project_data = {
                'project_id': project.id,
                'module_items': module_items
            }
            payload.append(project_data)

        data = {
            'project_items': payload,
            'meta': {
                'has_next': projects.has_next,
                'next_num': projects.next_num,
                'has_prev': projects.has_prev,
                'prev_num': projects.prev_num
            }
        }
        return data

    def to_reports_dict(self, page_num, per_page):
        reports = self.reports.paginate(page_num, per_page, False)
        reports_items = reports.items
        report_dicts = []
        for report in reports_items:
            report_dicts.append(report.to_dict())

        payload = {
            'testcase_id': self.id,
            'report_dicts': report_dicts,
            'meta': {
                'has_next': reports.has_next,
                'next_num': reports.next_num,
                'has_prev': reports.has_prev,
                'prev_num': reports.prev_num
            }
        }
        return payload


class TestStep(db.Model):
    __tablename__ = 'teststep'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    test_desc = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    api_id = db.Column(db.Integer, db.ForeignKey('api.id'))
    env_id = db.Column(db.Integer, db.ForeignKey('env.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    # suite_id = db.Column(db.Integer, db.ForeignKey('suite.id'))
    # testcase_id = db.Column(db.Integer, db.ForeignKey('testcase.id'))
    req_params = db.Column(db.Text())
    req_headers = db.Column(db.Text())
    req_cookies = db.Column(db.Text())
    req_body = db.Column(db.Text())
    reports = db.relationship('Report', backref='teststep', lazy='dynamic')

    def __repr__(self):
        return '<TestStep {}>'.format(self.name)

    def from_dict(self, data):
        user = g.current_user
        self.user_id = user.id

        for field in ['name', 'project_id', 'api_id', 'env_id', 'test_desc']:
            if field in data:
                if not data[field]:
                    print('null, bad request')

                setattr(self, field, data[field])

        for field in ['req_headers', 'req_cookies', 'req_params', 'req_body']:
            if field in data:
                payload = json.dumps(data_to_server(data.get(field)))
                setattr(self, field, payload)

        # self.api_id = data['api_id']
        #
        # if data['env_id']:
        #     self.env_id = data['env_id']

    def to_dict(self):
        req_headers = dict_to_obj(self.req_headers)
        req_cookies = dict_to_obj(self.req_cookies)
        req_params = dict_to_obj(self.req_params)
        req_body = dict_to_obj(self.req_body)
        api = Api.query.get_or_404(self.api_id)
        env = Env.query.get_or_404(self.env_id)
        project = Project.query.get_or_404(api.project_id)
        module = Module.query.get_or_404(api.module_id)
        user = User.query.get_or_404(self.user_id)
        report = self.reports.order_by(Report.timestamp.desc()).first()

        data = {
            'project': {'project_id': project.id, 'project_name': project.project_name},
            'module': {'module_id': module.id, 'module_name': module.module_name},
            'teststep_id': self.id,
            'teststep_name': self.name,
            'test_desc': self.test_desc,
            'user': {'user_id': self.user_id, 'user_name': user.username},
            'api': {'api_id': self.api_id, 'api_name': api.name, 'api_url': api.req_relate_url},
            'env': {'env_id': self.env_id,
                    'env_name': env.env_name,
                    'env_host': env.env_host,
                    'env_var': env.env_var,
                    'extracts': env.extracts,
                    'asserts': env.asserts},
            'timestamp': self.timestamp,
            'req_params': req_params,
            'req_headers': req_headers,
            'req_cookies': req_cookies,
            'req_body': req_body,
            'report_id': report.id if report else '',
            'report_result': str(report.test_result) if report else '',
            'report_time': report.timestamp.strftime('%Y/%m/%d %H:%M:%S') if report else ''
        }
        return data

    def to_reports_dict(self, page_num, per_page):
        reports = self.reports.paginate(page_num, per_page, False)
        reports_items = reports.items
        report_dicts = []
        for report in reports_items:
            report_dicts.append(report.to_dict())

        payload = {
            'teststep_id': self.id,
            'report_dicts': report_dicts,
            'meta': {
                'has_next': reports.has_next,
                'next_num': reports.next_num,
                'has_prev': reports.has_prev,
                'prev_num': reports.prev_num
            }
        }
        return payload


class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), default='undefined')
    summary = db.Column(db.Text)
    test_result = db.Column(db.Boolean)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    testcase_id = db.Column(db.Integer, db.ForeignKey('testcase.id'))
    teststep_id = db.Column(db.Integer, db.ForeignKey('teststep.id'))

    def __repr__(self):
        return '<Report {}>'.format(self.id)

    def from_dict(self, data):
        for field in ['summary', 'test_result', 'testcase_id', 'teststep_id']:
            if field in data:
                setattr(self, field, data[field])

        # self.testcase_id = data['testcase_id']

        if 'name' in data:
            self.name = data['name'] + '--%s' % datetime.utcnow().strftime('%Y/%m/%d %H:%M:%S')

    def to_dict(self):
        summary = ast.literal_eval(self.summary)

        data = {
            'report_id': self.id,
            'report_name': self.name,
            'summary': summary,
            'test_result': str(self.test_result),
            'timestamp': self.timestamp.strftime('%Y/%m/%d %H:%M:%S'),
            'testcase_id': self.testcase_id,
            'teststep_id': self.teststep_id
        }
        return data

