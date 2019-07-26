# -*- coding: utf8 -*-
from google.appengine.ext import ndb
from flask_login import UserMixin


class User(UserMixin, ndb.Model):
    username = ndb.StringProperty(required=True, indexed=True)  # id
    email = ndb.StringProperty(required=True)
    password = ndb.StringProperty(required=True)

    def get_id(self):
        return self.username


class Friend(ndb.Model):
    email = ndb.StringProperty(required=True)  # id
    nome = ndb.StringProperty(required=True)
    cognome = ndb.StringProperty(required=True)
    score = ndb.IntegerProperty(required=True, default=0)
    immagine_url = ndb.StringProperty()
    immagine_blob_key = ndb.BlobKeyProperty()


class Trip(ndb.Model):
    titolo = ndb.StringProperty(required=True)  # id
    data = ndb.DateProperty(required=True)
    partenza = ndb.StringProperty(required=True)
    destinazione = ndb.StringProperty(required=True)
    distanza = ndb.IntegerProperty(required=True)