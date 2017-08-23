#Flask
from flask import Flask, current_app
#Uploads
from flask_uploads import UploadSet, configure_uploads, IMAGES
#CCS Framework
from flask_bootstrap import Bootstrap
#Database
from flask_sqlalchemy import SQLAlchemy
#Login
from flask_login import LoginManager
from flask_moment import Moment


bootstrap = Bootstrap()
moment = Moment()
db = SQLAlchemy()

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'mainBlue.login'
photos = UploadSet('photos', IMAGES)

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    configure_uploads(app, photos)

    login_manager.init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)
    db.init_app(app)

    from .main import mainBlue
    app.register_blueprint(mainBlue)

    from .api import api
    app.register_blueprint(api, url_prefix='/api')
    
    with app.app_context():
        # create the database and the db table
        db.create_all()

    return app




