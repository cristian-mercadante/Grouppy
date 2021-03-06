# -*- coding: utf8 -*-

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, BooleanField
from wtforms.validators import InputRequired, Email, Length


class AddFriendForm(FlaskForm):
    email = StringField('Email', validators=[
        InputRequired(), Email(message="Email non valida."), Length(max=50)])
    nome = StringField('Nome', validators=[InputRequired(), Length(max=20)])
    cognome = StringField('Cognome', validators=[
                          InputRequired(), Length(max=20)])
    escludi = BooleanField('Escludi dalla classifica')
    submit = SubmitField('Aggiungi')


class EditFriendForm(FlaskForm):
    email = StringField('Email', validators=[
        InputRequired(), Email(message="Email non valida."), Length(max=50)])
    nome = StringField('Nome', validators=[InputRequired(), Length(max=20)])
    cognome = StringField('Cognome', validators=[
                          InputRequired(), Length(max=20)])
    escludi = BooleanField('Escludi dalla classifica')
    immagine = FileField('Immagine', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Modifica')
