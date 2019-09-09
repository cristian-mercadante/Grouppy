# -*- coding: utf8 -*-

from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, FloatField, DateField, SubmitField
from wtforms.validators import InputRequired, Length


def add_trip_form(friends, **kwargs):
    class AddTripForm(FlaskForm):
        titolo = StringField('Titolo', validators=[
            InputRequired(), Length(max=50)])
        data = DateField('Data', validators=[InputRequired()])
        partenza = StringField('Partenza', validators=[
            InputRequired(), Length(max=50)])
        destinazione = StringField('Destinazione', validators=[
            InputRequired(), Length(max=50)])
        distanza = FloatField('Distanza (km)', validators=[InputRequired()])
        ritorno = BooleanField('Andata e ritorno?')
        pagato = BooleanField(u'L\'autista è stato pagato?')
        speciale = BooleanField(u'Era un\'occasione speciale?')
        submit = SubmitField('Conferma')

    for f in friends:
        label_auto = 'auto' + str(f.key.id())
        label_pass = 'pass' + str(f.key.id())
        nomecogn = f.nome + ' ' + f.cognome
        field_auto = BooleanField(nomecogn)
        field_pass = BooleanField(nomecogn)
        setattr(AddTripForm, label_auto, field_auto)
        setattr(AddTripForm, label_pass, field_pass)
    return AddTripForm(**kwargs)
