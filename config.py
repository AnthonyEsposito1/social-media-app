class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    UPLOADED_PHOTOS_DEST = 'appl/static/img'
    SECRET_KEY = 'xxxxyyyyyzzzzz'
    TEMPLATES_AUTO_RELOAD = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///../DataBase.db'
    #SQLALCHEMY_ECHO = True

