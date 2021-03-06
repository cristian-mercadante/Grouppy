# -*- coding: utf8 -*-

import appengine_config

import logging

from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.config.from_object(__name__)
csrf_protect = CSRFProtect(app)

Bootstrap(app)

# LOGIN
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'user.login'
login_manager.login_message_category = 'info'

from app.models import User


@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('_404.html'), 404


# setting the secret key
if appengine_config.GAE_DEV:
    logging.warning('Using a dummy secret key')
    app.secret_key = 'my-secret-key'
    app.debug = True
else:
    import app_secrets
    app.secret_key = app_secrets.app_secret_key

from friend.routes import friend
from transazione.routes import transazione
from app.trip.routes import trip
from user.routes import user

app.register_blueprint(friend, url_prefix='/friend')
app.register_blueprint(transazione, url_prefix='/transazione')
app.register_blueprint(trip, url_prefix='/trip')
app.register_blueprint(user)
