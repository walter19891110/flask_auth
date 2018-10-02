from flask import Blueprint

token_api = Blueprint('token_api', __name__)

from . import my_token