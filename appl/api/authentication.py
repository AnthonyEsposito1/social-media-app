from flask import g, jsonify
from flask_login import current_app
from flask_httpauth import HTTPBasicAuth
from ..models import User, Anonymous
from . import api
from .errors import unauthorized


auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username_or_token, password):
    # first try to authenticate by token
    user = User.verify_auth_token(username_or_token)
    g.token_time_remaining = User.token_time_remaining(username_or_token)
    g.token_used = True
    if not user:
        # try to authenticate with username/password
        user = User.query.filter_by(username = username_or_token).first()
        g.token_time_remaining = None
        g.token_used = False
        if not user or not user.verify_password(password):
            return False
    g.current_user = user
    return True

@api.before_request
@auth.login_required
def before_request():
    pass
    
@auth.error_handler
def auth_error():
    return unauthorized('Invalid Credentials')

@api.route('/token')
def get_token():
    if g.token_used:
        return 'Cant use token to get a token'
    token = g.current_user.generate_auth_token(expiration=3600)
    return jsonify({'token': token, 'expiration': 3600})
