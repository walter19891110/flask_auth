from flask import Blueprint

dev_manager_api = Blueprint('dev_manager_api', __name__)

from . import device_manager
from . import api