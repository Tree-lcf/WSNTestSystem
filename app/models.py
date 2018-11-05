import base64
import os
from app import db
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask import g


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
    def to_collection_dict(page_num, per_page):
        users = User.query.paginate(page_num, per_page, False)
        data = {
            'users': [user.to_dict() for user in users.items],
            'meta': {
                'has_next': users.has_next,
                'next_num': users.next_num,
                'has_prev': users.has_prev,
                'prev_num': users.prev_num
            }
        }
        return data


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_name = db.Column(db.String(255), index=True, unique=True, nullable=False)
    owner_name = db.Column(db.String(255), index=True, nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.now)
    modules = db.relationship('Module', backref='project', lazy='dynamic')
    envs = db.relationship('Env', backref='project', lazy='dynamic')
    apis = db.relationship('Api', backref='project', lazy='dynamic')
    testcases = db.relationship('TestCase', backref='project', lazy='dynamic')
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
        data = {
            'project_id': self.id,
            'project_name': self.project_name,
            'project_owner': self.owner_name,
            'timestamp': self.timestamp,
            'modules': {
                'count': self.modules.count(),
                'list': [module.module_name for module in self.modules.order_by(Module.timestamp.desc()).all()]
            },
            'testcases_count': self.testcases.count(),
            'envs': {
                'count': self.envs.count(),
                'list': [env.id for env in self.envs.order_by(Env.timestamp.desc()).all()]
            },
            'users': {
                'count': self.users.count(),
                'list': [user.username for user in self.users.order_by(User.username).all()]
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


class Module(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    module_name = db.Column(db.String(255), index=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.now)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    apis = db.relationship('Api', backref='module', lazy='dynamic')

    def __repr__(self):
        return '<Module {}>'.format(self.module_name)

    def from_dict(self, data):
        for field in ['module_name', 'project_id']:
            if field in data:
                setattr(self, field, data[field])

    def to_dict(self):
        data = {
            'module_id': self.id,
            'module_name': self.module_name,
            'project_id': self.project_id,
            'timestamp': self.timestamp,
            'apis': {
                'count': self.apis.count(),
                'list': [api.api_name for api in self.apis.order_by(Api.timestamp.desc()).all()]
            }
        }
        return data


class Env(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    env_name = db.Column(db.String(255), index=True)
    env_desc = db.Column(db.Text())
    env_host = db.Column(db.String(255))
    env_var = db.Column(db.Text())
    extracts = db.Column(db.Text())
    asserts = db.Column(db.Text())
    timestamp = db.Column(db.DateTime, index=True, default=datetime.now)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    testcases = db.relationship('TestCase', backref='env', lazy='dynamic')
    teststeps = db.relationship('TestStep', backref='env', lazy='dynamic')

    def __repr__(self):
        return '<Env {}>'.format(self.env_name)

    def from_dict(self, data):
        for field in ['env_name', 'env_desc', 'env_host', 'env_var', 'extracts', 'asserts']:
            if field in data:
                setattr(self, field, data[field])

        if data['project_id']:
            self.project_id = data['project_id']

    def to_dict(self):
        data = {
            'env_id': self.id,
            'env_name': self.env_name,
            'project_id': self.project_id,
            'env_desc': self.env_desc,
            'env_host': self.env_host,
            'env_var': self.env_var,
            'extracts': self.extracts,
            'asserts': self.asserts,
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
    req_params = db.Column(db.Text())
    req_data_type = db.Column(db.String(255))
    req_body = db.Column(db.Text())
    timestamp = db.Column(db.DateTime, index=True, default=datetime.now)
    module_id = db.Column(db.Integer, db.ForeignKey('module.id'))
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    testcases = db.relationship('TestCase', backref='api', lazy='dynamic')
    teststeps = db.relationship('TestStep', backref='api', lazy='dynamic')

    def __repr__(self):
        return '<Api {}>'.format(self.name)

    def from_dict(self, data):
        for field in ['name', 'req_method', 'req_temp_host', 'req_relate_url',
                      'req_headers', 'req_params', 'req_data_type', 'req_body']:
            if field in data:
                setattr(self, field, data[field])

        if data['module_id']:
            self.module_id = data['module_id']

        if data['project_id']:
            self.project_id = data['project_id']

    def to_dict(self):
        data = {
            'api_id': self.id,
            'name': self.name,
            'project_id': self.project_id,
            'module_id': self.module_id,
            'req_method': self.req_method,
            'req_temp_host': self.req_temp_host,
            'req_relate_url': self.req_relate_url,
            'req_headers': self.req_headers,
            'req_params': self.req_params,
            'req_data_type': self.req_data_type,
            'req_body': self.req_body,
            'timestamp': self.timestamp,
            'testcases': {
                'count': self.testcases.count(),
                'list': [testcase.name for testcase in self.testcases.order_by(TestCase.timestamp.desc()).all()]
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
                    'api_list': api_list
                }
                module_list.append(module_data)
            project_data = {
                'project_id': project.id,
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


class TestCase(db.Model):
    __tablename__ = 'testcase'
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    api_id = db.Column(db.Integer, db.ForeignKey('api.id'))
    name = db.Column(db.String(255))
    test_desc = db.Column(db.String(255))
    env_id = db.Column(db.Integer, db.ForeignKey('env.id'))
    teststeps = db.Column(db.Text())  # [teststep_id...]
    test_result = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.now)
    report = db.relationship('Report', backref='testcase', uselist=False)

    def __repr__(self):
        return '<TestCase {}>'.format(self.name)

    def from_dict(self, data):
        for field in ['name', 'test_desc', 'teststeps']:
            if field in data:
                setattr(self, field, data[field])

        if data['project_id']:
            self.project_id = data['project_id']

        if data['api_id']:
            self.api_id = data['api_id']

        if data['env_id']:
            self.env_id = data['env_id']

    def to_dict(self):
        api = Api.query.get(self.api_id)
        env = Env.query.get(self.env_id)
        data = {
            'testcase_id': self.id,
            'name': self.name,
            'test_desc': self.test_desc,
            'project_name': Project.query.get(self.project_id).project_name,
            'module_name': Module.query.get(Api.query.get(self.api_id).module_id).module_name,
            'api_name': api.name,
            'api_url': api.req_relate_url,
            'env_name': env.env_name,
            'env_host': env.env_host,
            'env_var': env.env_var,
            'extracts': env.extracts,
            'asserts': env.asserts,
            'teststeps': self.teststeps,
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


class TestStep(db.Model):
    __tablename__ = 'teststep'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.now)
    api_id = db.Column(db.Integer, db.ForeignKey('api.id'))
    env_id = db.Column(db.Integer, db.ForeignKey('env.id'))
    req_params = db.Column(db.Text())
    req_headers = db.Column(db.Text())
    req_cookies = db.Column(db.Text())
    req_body = db.Column(db.Text())

    def __repr__(self):
        return '<TestStep {}>'.format(self.id)

    def from_dict(self, data):
        for field in ['req_params', 'req_headers', 'req_cookies', 'req_body']:
            if field in data:
                setattr(self, field, data[field])

        self.api_id = data['api_id']

        if data['env_id']:
            self.env_id = data['env_id']

    def to_dict(self):
        data = {
            'teststep_id': self.id,
            'api_id': self.api_id,
            'env_id': self.env_id,
            'timestamp': self.timestamp,
            'req_params': self.req_params,
            'req_headers': self.req_headers,
            'req_cookies': self.req_cookies,
            'req_body': self.req_body,
        }
        return data


class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    report_name = db.Column(db.String(255))
    is_success = db.Column(db.Boolean, default=False)
    summary = db.Column(db.Text)
    detail = db.Column(db.Text)
    duration = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.now)
    testcase_id = db.Column(db.Integer, db.ForeignKey('testcase.id'))

    def __repr__(self):
        return '<Report {}>'.format(self.report_name)
