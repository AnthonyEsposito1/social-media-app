from flask import g
from . import db, login_manager 
#Database
from flask_login import UserMixin, current_app, AnonymousUserMixin
from sqlalchemy import func
#WSGI utility library for Python
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)
from datetime import datetime, timedelta

following_table=db.Table('following_table',                            
                             db.Column('group_id', db.Integer,db.ForeignKey('groups.id')),
                             db.Column('user_id',db.Integer,db.ForeignKey('users.id'))
                             )

class Group(db.Model):
    __tablename__ = 'groups'
    id = db.Column(db.Integer, primary_key=True)
    group_name = db.Column(db.String(64), unique=True, index=True)

    def __repr__(self):
        return '<Group %r>' % self.group_name
    
class ScoreTable(db.Model):
    __tablename__ = 'score_table'
    users_id= db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    pics_id = db.Column(db.Integer, db.ForeignKey('pics.id'), primary_key=True)
    score = db.Column(db.Integer)
    child = db.relationship("Pic")


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    pics = db.relationship('Pic', backref='Pics', lazy='dynamic')
    groupers = db.relationship('Group', secondary=following_table, backref=db.backref('grouped', lazy='dynamic'))
    children = db.relationship("ScoreTable", foreign_keys=[ScoreTable.users_id],
                               backref=db.backref('test', lazy='joined'),lazy='dynamic',cascade='all, delete-orphan')


    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)


    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def generate_auth_token(self, expiration):
        s = Serializer(current_app.config['SECRET_KEY'],expires_in=expiration)
        return s.dumps({'id': self.id}).decode('ascii')

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)            
        except SignatureExpired as e:
            print(e.message)
            return None
        except BadSignature:
            print("Bad Signature")
            return None
        user = User.query.get(data['id'])
        return user

    def token_time_remaining(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token, return_header=True)
        except SignatureExpired:
            return None
        except BadSignature:
            return None
        data = s.loads(token, return_header=True)
        token_time_remaining=(data[1]['exp'] - s.now())
        return token_time_remaining

    def __repr__(self):
        return '<User: %r, User Id %r>' % (self.username, self.id)

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    location = db.Column(db.Text)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))


class Anonymous(AnonymousUserMixin):
    def __init__(self):
        self.username = 'Stranger'

login_manager.anonymous_user = Anonymous

class Pic(db.Model):
    __tablename__ = 'pics'
    id = db.Column(db.Integer, primary_key=True)
    picscore = db.Column(db.Integer)
    pic_location = db.Column(db.String(64), unique=False, index=True)
    pic_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    child2 = db.relationship("ScoreTable", foreign_keys=[ScoreTable.pics_id],
                               backref=db.backref('test2', lazy='joined'),lazy='dynamic',cascade='all, delete-orphan')

    @staticmethod
    def str_format(string):
        info = string
        index = info.rfind('.')
        fronthalf = info[:index]
        backhalf = info[index:]
        pic_location = fronthalf.replace('static/img/','')+backhalf.replace('.','\\.')
     
        return pic_location

    def score_get(self):
        togglelist2 = []
        togglelist3 = []
        scoreX = ScoreTable.query.with_entities(ScoreTable.pics_id, func.sum(ScoreTable.score)).group_by(ScoreTable.pics_id).all()
        pic_scoreFlat = [var[0] for var in scoreX]
        pic_scoreFlat2 = [var[1] for var in scoreX]

        for x in pic_scoreFlat:
            loc = Pic.query.filter_by(id=x).first()
            pic_location = self.str_format(loc.pic_location)
            togglelist2.append(pic_location)
            
        toggleFlat = zip(togglelist2, pic_scoreFlat2)
        for x in toggleFlat:
            togglelist3.append(x)
            
        return togglelist3

    def __repr__(self):
        return '<Pic Id: %r>' % self.id


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


