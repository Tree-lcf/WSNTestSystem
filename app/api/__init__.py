from flask import Blueprint

bp = Blueprint('api', __name__)

from app.api import projects, users, modules, envs, apis, testcases, teststeps