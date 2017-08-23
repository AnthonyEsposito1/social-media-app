#Flask
from flask import render_template, redirect, request, url_for, flash
#Logins
from flask_login import login_user, logout_user, login_required, current_user
#Operating system dependent functionality
import os
#local imports
from .. import db, photos
from ..models import User, Post, Pic, Group, ScoreTable
from . import mainBlue
from .forms import LoginForm, RegistrationForm, ChangePasswordForm, PhotoForm, photos, PostForm, GroupForm
import pprint
import json
import requests
from sqlalchemy import func


@mainBlue.route('/group/<group_name>')
@login_required
def group_page(group_name):
    
    user = current_user._get_current_object()
    group = Group.query.filter_by(group_name=group_name).first()
    group2 = Group.query.filter(Group.grouped.any(username=user.username)).all()
    for x in group2:
        if (x.group_name == group_name):
            flash('Already a member of ' + group_name)
            return redirect(url_for('mainBlue.group'))
    group.grouped.append(user)
    db.session.commit()
    flash('Added to group: ' + group_name)
    return redirect(url_for('mainBlue.group'))


@mainBlue.route('/group/remove/<group_name>')
@login_required
def group_page_remove(group_name):
    
    user = current_user._get_current_object()
    group = Group.query.filter_by(group_name=group_name).first()
    user1 = Group.query.filter(Group.grouped.any(username=user.username))\
            .filter_by(group_name=group_name).all()

    if user1 == []:
        flash('Not a member of: ' + group_name)
        return redirect(url_for('mainBlue.group'))
    else:
        group.grouped.remove(user)
        db.session.commit()
        flash('Removed: ' + group_name)
        return redirect(url_for('mainBlue.group'))


@mainBlue.route('/groups', methods=['GET', 'POST'])
@login_required
def group():
    list1=[]
    list2=[]
    list3=[]
    form = GroupForm()
    if form.validate_on_submit():
        group = Group(group_name=form.name.data)
        db.session.add(group)
        db.session.commit()
        flash('Group Added.') 
        return redirect(url_for('mainBlue.group'))
    group = Group.query.order_by(Group.group_name).all()
    user = current_user._get_current_object()
    group2 = Group.query.filter(Group.grouped.any(username=user.username)).all()
    
    for x in group2:
        list1.append(x.group_name)
    for x in group:
        list2.append(x.group_name)
    list1.sort()
    list2.sort() 
    for x in list2:
        if x in list1:
            list3.append("(Following)")
        else:
            list3.append("(Not following)")
    
    return render_template('groups.html', form=form, group=group, list1=list1, list2=list2, list3=list3)

@mainBlue.route('/', methods=['GET', 'POST'])
def index():
    if User.query.filter_by(username="tony").first():
        return render_template('index.html')
    else:  
        user = User(username="tony",password="tony")
        db.session.add(user)
        db.session.commit()
        return render_template('index.html')

@mainBlue.route('/post', methods=['GET', 'POST'])
@login_required
def indexPost():
    form = PostForm()
    if form.validate_on_submit():
        send_url = 'http://freegeoip.net/json/'
        ip = request.remote_addr
        #ip = '66.8.193.155'
        send_url_ip = send_url + ip
        r = requests.get(send_url_ip)
        j = json.loads(r.text)
        location = ("%s, %s" % (j['city'], j['region_code']))
        post = Post(body=form.body.data,location=location,author=current_user._get_current_object())
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('mainBlue.indexPost'))   
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('indexPost.html', form=form, posts=posts)

@mainBlue.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    pic = Pic.query.join(User).filter_by(id=user.id).all()
    posts = user.posts.order_by(Post.timestamp.desc()).all()
    group = Group.query.filter(Group.grouped.any(username=username)).all()
    score = ScoreTable.query.with_entities(func.sum(ScoreTable.score)).join(Pic).group_by(Pic.pic_id).filter_by(pic_id=user.id).all()
    return render_template('user.html', user=user, posts=posts, pic=pic, group=group, score=score)

@mainBlue.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('mainBlue.index'))
        flash('Invalid username or password.')
    return render_template('auth/login.html', form=form)

@mainBlue.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('mainBlue.index'))

@mainBlue.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data,password=form.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('mainBlue.login'))
    return render_template('auth/register.html', form=form)

@mainBlue.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            db.session.commit()
            flash('Your password has been updated.')
            return redirect(url_for('mainBlue.index'))
        else:
            flash('Invalid password.')
    return render_template("auth/change_password.html", form=form)

@mainBlue.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    form = PhotoForm()
    if form.validate_on_submit():
        filename = photos.save(form.photo.data)
        pic = Pic(pic_location='static/img/%s' % filename,Pics=current_user._get_current_object())
        db.session.add(pic)
        db.session.commit()
        flash('File Uploaded. (%s)' % filename)
        return redirect(url_for('mainBlue.upload'))
    return render_template('upload.html', form=form)


@mainBlue.route('/show', methods=['GET', 'POST'])
@login_required
def show():
    path = "appl/static/img"    
    return render_template('show.html',path=path,os=os)

@mainBlue.route('/show2', methods=['GET', 'POST'])
@login_required
def show2():
    path = "appl/static/img"
    for x in os.listdir(path):
        pic = Pic(pic_location='static/img/%s' % x)
        #db.session.add(pic)
        #db.session.commit()
        print('static/img/%s' % x)
    return "show2"


@mainBlue.route('/test')
@login_required
def test():
    x = ScoreTable.query.with_entities(func.sum(ScoreTable.score), Pic.pic_id).join(Pic).group_by(Pic.pic_id).filter_by(pic_id=3).all()
    for y in x:
        print('UserId: %s UserScore: %s'  % (y[1],y[0]))   
    return "test"

@mainBlue.route('/test2/<pic_location>', methods=['POST','GET'])
def test2(pic_location):
    user = current_user._get_current_object()
    pic_location = 'static/img/' + pic_location
    print(pic_location)#static/img/A.jpg
    pic = Pic.query.filter_by(pic_location=pic_location).first()
    #print(pic)
    #f = ScoreTable(test2=pic,test=user, score=5)
    #db.session.add(f)
    #db.session.commit()
    return render_template('test.html')


@mainBlue.route('/api/register', methods=['POST'])
def register2():
    if not request.json or not 'username' in request.json:
        return "Data Format Error!"
    else:
        if User.query.filter_by(username=username).first():
            return "Username already in use."
        user = User(username=username,password=password)
        db.session.add(user)
        db.session.commit()
        return "User Added"
        
@mainBlue.route('/test3')
def test3():
    p = Pic.query.get_or_404(1)
    #print(p)
    for q in p.child2.all():
        pprint.pprint(vars(q))

    return "test3"


@mainBlue.route('/test4')
def test4():
    return render_template('test4.html')


#voting system--------------------------------------------------------------------------------------------
@mainBlue.route('/picscore', methods=['POST', 'GET'])
@login_required
def picscore():
    if request.method == 'GET':
        #print(json.dumps(Pic().score_get()))
        return json.dumps(Pic().score_get())
#---------------------------------------------
    elif request.method == 'POST':
  
        info = request.json['VOTE'].split( )#request.data
        if info[1] == 'upvote':
            formatinfo  = info[2].replace('up','',1)
            
        elif info[1] == 'downvote':
            formatinfo = info[2].replace('down','',1)
            
        state = int(info[0])
        user = current_user._get_current_object()
        pic_location = 'static/img/' + formatinfo
        pic = Pic.query.filter_by(pic_location=pic_location).first()
        scoreacc = ScoreTable.query.filter_by(users_id=user.id,pics_id=pic.id).first()

        if scoreacc:
            scoreacc.score = state
            
            if scoreacc.score ==  0:
                db.session.delete(scoreacc)
                db.session.commit()
            
            db.session.commit()
        else:
            f = ScoreTable(test2=pic,test=user, score=state)
            db.session.add(f)
            db.session.commit()

        return '1Success1'


@mainBlue.route('/show3', methods=['POST', 'GET'])
@login_required
def new_show():
    togglelist = []
    img = []
    
    path = "appl/static/img"

    for piclinks in os.listdir(path):
        img.append(piclinks)
    
    user = current_user._get_current_object()
    scoreall = ScoreTable.query.filter_by(users_id=user.id).all()
    for data in scoreall:
        pic = Pic.query.filter_by(id=data.pics_id).first()
    
        if data.score == 1:
            direction = 'up'
        elif data.score == -1:
            direction = 'down'
        pic_location = Pic.str_format(pic.pic_location)
        toggle = '.'+direction+pic_location
        togglelist.append(toggle)
   
    togglelist = ', '.join(togglelist)
    
    return render_template('show454.html',img=img, togglelist=togglelist)

#voting system--------------------------------------------------------------------------------------------

