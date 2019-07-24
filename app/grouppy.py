import appengine_config

import logging

from flask import Flask, url_for
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
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from app.models import User


@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)


# setting the secret key
if appengine_config.GAE_DEV:
    logging.warning('Using a dummy secret key')
    app.secret_key = 'my-secret-key'
    app.debug = True
else:
    import app_secrets
    app.secret_key = app_secrets.app_secret_key

from app import routes
