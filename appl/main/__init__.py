from flask import Blueprint

mainBlue = Blueprint('mainBlue', __name__)

from . import views
