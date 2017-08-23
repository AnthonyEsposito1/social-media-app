from flask import jsonify, request, current_app, url_for, g, jsonify
from . import api
from ..models import User, Post, Pic, Group, ScoreTable
from sqlalchemy import func
from .. import db
import json


@api.route('/users')
def get_user():
    list1={}
    user = User.query.all()
    for x in user:
        list1[str(x.id)] = x.username
    list1.update({'token_time_remaining':str(g.token_time_remaining)})
    return jsonify(list1)

@api.route('/groups')
def get_user_group():
    list1=[]
    group = Group.query.filter(Group.grouped.any(username=g.current_user.username)).all()
    for name in  group:
        list1.append(name.group_name)
    return jsonify(list1)


@api.route('/user_data')
def get_user_data():
    user = User.query.filter_by(username=g.current_user.username).first_or_404()
    pic = Pic.query.join(User).filter_by(id=user.id).all()
    posts = user.posts.order_by(Post.timestamp.desc()).all()
    group = Group.query.filter(Group.grouped.any(username=g.current_user.username)).all()
    score = ScoreTable.query.with_entities(func.sum(ScoreTable.score)).join(Pic).group_by(Pic.pic_id).filter_by(pic_id=user.id).all()
    if not score:
        x = 0
    else:
        x = score[0][0]
    return jsonify({'%s:%s' % (g.current_user.username,g.current_user.id):
        {
        'Groups': [groups.group_name for groups in group],
        'Posts': [post.body for post in posts],
        'Images': ['http://localhost:5006/%s' % (pics.pic_location) for pics in pic],
        'ToatalScore' : x
        }
        })










