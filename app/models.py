import base64
import os
from app import db
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

user_project = db.Table('user_project',
                        db.Column('user_id', db.Integer, db.ForeignKey('user.id'), nullable=False),
                        db.Column('project_id', db.Integer, db.ForeignKey('project.id'), nullable=False)
                        )


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True)
    email = db.Column(db.String(255), unique=True)
    password_hash = db.Column(db.String(128))
    is_administrator = db.Column(db.Boolean, default=False)
    token = db.Column(db.String(32), index=True, unique=True)
    token_expiration = db.Column(db.DateTime)
    projects = db.relationship(
        'Project', secondary=user_project,
        backref=db.backref('user', lazy='dynamic'), lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def add(self):
        db.session.add(self)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())

    def to_dict(self):
        data = {
            'id': self.id,
            'username': self.username,
            'is_administrator': self.is_administrator,
            'projects': self.projects.all()
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


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_name = db.Column(db.String(255), unique=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.now)
    modules = db.relationship('Module', backref='project', lazy='dynamic')
    envs = db.relationship('Env', backref='project', lazy='dynamic')
    scenes = db.relationship('Scene', backref='project', lazy='dynamic')

    def __repr__(self):
        return '<Project {}>'.format(self.name)

    def to_dict(self):
        data = {
            'id': self.id,
            'project_name': self.project_name,
            'timestamp': self.timestamp,
            'module_count': self.modules.count(),
            'scenes_count': self.scenes.count(),
            'envs_count': self.envs.count()
        }
        return data


class Module(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    module_name = db.Column(db.String(255), unique=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.now)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    apis = db.relationship('Api', backref='module', lazy='dynamic')

    def __repr__(self):
        return '<Module {}>'.format(self.name)


class Env(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    env_name = db.Column(db.String(255))
    env_version = db.Column(db.String(255))
    env_host = db.Column(db.String(255))
    env_var = db.Column(db.Text())
    env_param = db.Column(db.Text())
    env_repeat = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.now)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    tests = db.relationship('Test', backref='env', lazy='dynamic')

    def __repr__(self):
        return '<Env {}>'.format(self.name)


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