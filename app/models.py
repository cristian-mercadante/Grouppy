# -*- coding: utf8 -*-
from google.appengine.ext import ndb
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from grouppy import app


class User(UserMixin, ndb.Model):
    username = ndb.StringProperty(required=True, indexed=True)  # id
    email = ndb.StringProperty(required=True)
    password = ndb.StringProperty(required=True)
    cassa = ndb.FloatProperty(default=0)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.username}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.get_by_id(user_id)

    def get_id(self):
        return self.username


class Friend(ndb.Model):
    email = ndb.StringProperty(required=True)
    nome = ndb.StringProperty(required=True)
    cognome = ndb.StringProperty(required=True)
    score = ndb.FloatProperty(required=True, default=0)
    immagine_url = ndb.StringProperty()
    immagine_blob_key = ndb.BlobKeyProperty()


class Trip(ndb.Model):
    titolo = ndb.StringProperty(required=True)
    data = ndb.DateProperty(required=True)
    partenza = ndb.StringProperty(required=True)
    destinazione = ndb.StringProperty(required=True)
    distanza = ndb.FloatProperty(required=True)
    ritorno = ndb.BooleanProperty(default=False)
    pagato = ndb.BooleanProperty(default=False)
    speciale = ndb.BooleanProperty(default=False)
    autisti = ndb.IntegerProperty(repeated=True)
    passeggeri = ndb.IntegerProperty(repeated=True)
    score_total = ndb.FloatProperty(required=True)


class Transazione(ndb.Model):
    titolo = ndb.StringProperty(required=True)
    descrizione = ndb.StringProperty()
    data = ndb.DateProperty(required=True)
    costo = ndb.FloatProperty(required=True)
