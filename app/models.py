# -*- coding: utf8 -*-
from google.appengine.ext import ndb
from flask_login import UserMixin

# class Color(ndb.Model):
#    label = ndb.StringProperty(required=True, indexed=True)
#    red = ndb.IntegerProperty(required=True)
#    green = ndb.IntegerProperty(required=True)
#    blue = ndb.IntegerProperty(required=True)


class User(UserMixin, ndb.Model):
    username = ndb.StringProperty(required=True, indexed=True)
    email = ndb.StringProperty(required=True)
    password = ndb.StringProperty(required=True)

    def get_id(self):
        return self.username
