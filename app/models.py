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
            'id': self.id,
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
    scenes = db.relationship('Scene', backref='project', lazy='dynamic')
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
            'id': self.id,
            'project_name': self.project_name,
            'project_owner': self.owner_name,
            'timestamp': self.timestamp,
            'modules': {
                'count': self.modules.count(),
                'list': [module.module_name for module in self.modules.order_by(Module.timestamp.desc()).all()]
            },
            'scenes_count': self.scenes.count(),
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
            'id': self.id,
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
    env_version = db.Column(db.String(255), index=True)
    env_host = db.Column(db.String(255))
    env_var = db.Column(db.Text())
    env_param = db.Column(db.Text())
    env_repeat = db.Column(db.Integer, default=1)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.now)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    tests = db.relationship('Test', backref='env', lazy='dynamic')

    def __repr__(self):
        return '<Env {}>'.format(self.env_name)

    def from_dict(self, data):
        for field in ['env_name', 'env_version', 'env_host',
                      'env_var', 'env_param', 'env_repeat']:
            if field in data:
                setattr(self, field, data[field])

        if data['project_name']:
            self.project_id = Project.query.filter_by(project_name=data['project_name']).first().id

    def to_dict(self):
        data = {
            'id': self.id,
            'env_name': self.env_name,
            'project_id': self.project_id,
            'env_version': self.env_version,
            'env_host': self.env_host,
            'env_var': self.env_var,
            'env_param': self.env_param,
            'env_repeat': self.env_repeat,
            'timestamp': self.timestamp,
            'tests': {
                'count': self.tests.count(),
                'list': [test.test_name for test in self.tests.order_by(Test.timestamp.desc()).all()]
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
    api_name = db.Column(db.String(255))
    req_method = db.Column(db.String(255))
    req_relat_url = db.Column(db.String(255))
    req_headers = db.Column(db.String(255))
    req_params = db.Column(db.Text())
    req_data_type = db.Column(db.String(255))
    req_body = db.Column(db.Text())
    timestamp = db.Column(db.DateTime, index=True, default=datetime.now)
    module_id = db.Column(db.Integer, db.ForeignKey('module.id'))
    tests = db.relationship('Test', backref='api', lazy='dynamic')

    def __repr__(self):
        return '<Api {}>'.format(self.name)


class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    test_name = db.Column(db.String(255))
    test_desc = db.Column(db.String(255))
    req_method = db.Column(db.String(255))
    req_abs_url = db.Column(db.String(255))
    req_headers = db.Column(db.String(255))
    req_params = db.Column(db.Text())
    req_data_type = db.Column(db.String(255))
    req_body = db.Column(db.Text())
    extracts = db.Column(db.Text())
    asserts = db.Column(db.Text())
    skip_status = db.Column(db.String(255))
    test_result = db.Column(db.String(255))
    test_type = db.Column(db.String(255))
    test_sn = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.now)
    api_id = db.Column(db.Integer, db.ForeignKey('api.id'))
    env_id = db.Column(db.Integer, db.ForeignKey('env.id'))
    scene_id = db.Column(db.Integer, db.ForeignKey('scene.id'))
    report = db.relationship('Report', backref='test', uselist=False)

    def __repr__(self):
        return '<Test {}>'.format(self.name)


class Scene(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    scene_name = db.Column(db.String(255))
    scene_desc = db.Column(db.String(255))
    scene_ver = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.now)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    env_id = db.Column(db.Integer, db.ForeignKey('env.id'))
    tests = db.relationship('Test', backref='scene', lazy='dynamic')

    def __repr__(self):
        return '<Scene {}>'.format(self.name)


class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    report_name = db.Column(db.String(255))
    is_success = db.Column(db.Boolean, default=False)
    summary = db.Column(db.Text)
    detail = db.Column(db.Text)
    duration = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.now)
    test_id = db.Column(db.Integer, db.ForeignKey('test.id'))

    def __repr__(self):
        return '<Report {}>'.format(self.name)