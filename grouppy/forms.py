from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length, ValidationError
from grouppy.models import User
from werkzeug.security import check_password_hash
from flask_login import login_user


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[
                           InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[
                             InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('Remember Me')

    def __init__(self, *k, **kk):
        self._user = None
        super(LoginForm, self).__init__(*k, **kk)

    def validate(self):
        self._user = User.query.filter_by(
            username=self.username.data).first()
        return super(LoginForm, self).validate()

    def validate_username(self, username):
        if self._user is None:
            raise ValidationError("Username not recognized.")

    def validate_password(self, password):
        if self._user is None:
            raise ValidationError()
        if not check_password_hash(self._user.password, self.password.data):
            raise ValidationError("Password does not match.")

    def log_in(self):
        if self.validate_on_submit():
            login_user(self._user, remember=self.remember.data)
            return True
        return False


class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[
        InputRequired(), Email(message="Invalid Email."), Length(max=50)])
    username = StringField('Username', validators=[
        InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[
        InputRequired(), Length(min=8, max=80)])

    def validate_username(self, username):
        user = User.query.filter_by(username=self.username.data).first()
        if user:
            raise ValidationError('That username is taken.')

    def validate_email(self, email):
        email = User.query.filter_by(email=self.email.data).first()
        if email:
            raise ValidationError('That email is taken.')
