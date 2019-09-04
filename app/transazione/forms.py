# -*- coding: utf8 -*-

from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, DateField, SubmitField
from wtforms.validators import InputRequired, Length


class TransazioneForm(FlaskForm):
    titolo = StringField('Titolo', validators=[
                         InputRequired(), Length(max=50)])
    data = DateField('Data', validators=[InputRequired()], format='%Y-%m-%d')
    costo = FloatField('Costo', validators=[InputRequired()])
    descrizione = StringField('Descrizione', validators=[Length(max=300)])
    submit = SubmitField('Applica')
