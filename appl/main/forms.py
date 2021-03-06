#Froms
from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import Required, Length, Regexp, EqualTo
from flask_wtf.file import FileAllowed, FileRequired, FileField
from wtforms import ValidationError
from ..models import User
from .. import photos



class LoginForm(Form):
    username = StringField('Username', validators=[Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,'Usernames must have only letters, ''numbers, dots or underscores')])
    password = PasswordField('Password', validators=[Required()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')

class RegistrationForm(Form):
    username = StringField('Username', validators=[Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,'Usernames must have only letters, ''numbers, dots or underscores')])
    password = PasswordField('Password', validators=[Required(), EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField('Confirm password', validators=[Required()])
    submit = SubmitField('Register')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')

class ChangePasswordForm(Form):
    old_password = PasswordField('Old password', validators=[Required()])
    password = PasswordField('New password', validators=[Required(), EqualTo('password2', message='Passwords must match')])
    password2 = PasswordField('Confirm new password', validators=[Required()])
    submit = SubmitField('Update Password')

class PhotoForm(Form):
    photo = FileField('Your photo', validators=[FileRequired(), FileAllowed(photos, 'Images only!')])
    submit = SubmitField('Upload')

 
class PostForm(Form):
    body = TextAreaField("Write how much you hate lou!", validators=[Required()])
    submit = SubmitField('Submit')

class GroupForm(Form):
    name = StringField("Group name!", validators=[Required()])
    submit = SubmitField('Submit')

