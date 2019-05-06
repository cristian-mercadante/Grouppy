from flask import Flask, url_for
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

import os
db_path = os.path.abspath(os.getcwd()) + "\database.db"

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Thisissupposedtobesecret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
csrf_protect = CSRFProtect(app)
Bootstrap(app)
db = SQLAlchemy(app)

# LOGIN
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from grouppy.models import User


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


from grouppy import routes
