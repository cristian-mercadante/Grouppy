# -*- coding: utf8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import InputRequired, Email, Length, ValidationError
from werkzeug.security import check_password_hash
from flask_login import login_user, current_user
from app.models import User
from werkzeug.security import generate_password_hash


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[
                           InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[
                             InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('Ricordami')
    submit = SubmitField('Accedi')

    def __init__(self, *k, **kk):
        self._user = None
        super(LoginForm, self).__init__(*k, **kk)

    def validate(self):
        self._user = User.get_by_id(self.username.data)
        return super(LoginForm, self).validate()

    def validate_username(self, username):
        if self._user is None:
            raise ValidationError("Username non riconosciuto.")

    def validate_password(self, password):
        if self._user is None:
            raise ValidationError()
        if not check_password_hash(self._user.password, self.password.data):
            raise ValidationError("La password non corrisponde.")

    def log_in(self):
        if self.validate_on_submit():
            login_user(self._user, remember=self.remember.data)
            return True
        return False


class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[
        InputRequired(), Email(message="Email non valida."), Length(max=50)])
    username = StringField('Username', validators=[
        InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[
        InputRequired(), Length(min=8, max=80)])
    confirm_password = PasswordField('Conferma password', validators=[
        InputRequired(), Length(min=8, max=80)])
    submit = SubmitField('Iscriviti')

    def validate_username(self, username):
        user = User.get_by_id(self.username.data)
        if user:
            raise ValidationError(u'Username già in uso.')

    def validate_email(self, email):
        email = User.query(User.email == self.email.data).fetch(1)
        if email:
            raise ValidationError(u'Email già in uso.')

    def validate_password(self, password):
        if self.password.data != self.confirm_password.data:
            raise ValidationError('Le password sono diverse.')


class ChangeEmailForm(FlaskForm):
    email = StringField('Email', validators=[
        InputRequired(), Email(message="Email non valida."), Length(max=50)])
    submit = SubmitField('Conferma')

    def validate_email(self, email):
        email = User.query(User.email == self.email.data).fetch(1)
        if email:
            raise ValidationError(u'Email già in uso.')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Vecchia Password', validators=[
        InputRequired(), Length(min=8, max=80)])
    new_password = PasswordField('Nuova Password', validators=[
        InputRequired(), Length(min=8, max=80)])
    confirm_password = PasswordField('Conferma password', validators=[
        InputRequired(), Length(min=8, max=80)])
    submit = SubmitField('Cambia')

    def validate_old_password(self, old_password):
        if not check_password_hash(current_user.password, self.old_password.data):
            raise ValidationError("La vecchia password non corrisponde.")

    def validate_new_password(self, new_password):
        if self.new_password.data != self.confirm_password.data:
            raise ValidationError('Le password sono diverse.')
