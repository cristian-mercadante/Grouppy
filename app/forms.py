# -*- coding: utf8 -*-

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, BooleanField, FloatField, DateField, SelectMultipleField
from wtforms.validators import InputRequired, Email, Length, ValidationError
from app.models import User, Friend
from werkzeug.security import check_password_hash
from flask_login import login_user, current_user


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[
                           InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[
                             InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('Ricordami')

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
            raise ValidationError('La password sono diverse.')


class AddFriendForm(FlaskForm):
    email = StringField('Email', validators=[
        InputRequired(), Email(message="Email non valida."), Length(max=50)])
    nome = StringField('Nome', validators=[InputRequired(), Length(max=20)])
    cognome = StringField('Cognome', validators=[
                          InputRequired(), Length(max=20)])


class AddTripForm(FlaskForm):
    titolo = StringField('Titolo', validators=[
                         InputRequired(), Length(max=50)])
    data = DateField('Data', validators=[InputRequired()])
    partenza = StringField('Partenza', validators=[
                           InputRequired(), Length(max=50)])
    destinazione = StringField('Destinazione', validators=[
                               InputRequired(), Length(max=50)])
    distanza = FloatField('Distanza (km)', validators=[InputRequired()])

    # friends = Friend.query(ancestor=ndb.Key(User, current_user)).fetch()
    # autisti = SelectMultipleField(
    #   'Autisti',
    # choices=friends,
    #  validators = [InputRequired()])

    def validate_titolo(self, titolo):
        trip = Trip.get_by_id(self.titolo.data, parent=current_user.key)
        if trip:
            raise ValidationError(u'Titolo già in uso.')


class UserSettingsForm(FlaskForm):
    email = StringField('Email', validators=[
        InputRequired(), Email(message="Email non valida."), Length(max=50)])

    def validate_email(self, email):
        email = User.query(User.email == self.email.data).fetch(1)
        if email:
            raise ValidationError(u'Email già in uso.')


class EditFriendForm(FlaskForm):
    email = StringField('Email', validators=[
        InputRequired(), Email(message="Email non valida."), Length(max=50)])
    nome = StringField('Nome', validators=[InputRequired(), Length(max=20)])
    cognome = StringField('Cognome', validators=[
                          InputRequired(), Length(max=20)])
    immagine = FileField('Immagine', validators=[
                         FileRequired(), FileAllowed(['jpg', 'png'])])
