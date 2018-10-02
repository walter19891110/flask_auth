from flask import Blueprint

user_manager_api = Blueprint('user_manager_api', __name__)

from . import user_manager
