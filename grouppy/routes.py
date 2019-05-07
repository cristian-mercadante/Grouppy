from flask import render_template, url_for, redirect
from grouppy import app, db
from grouppy.forms import RegisterForm, LoginForm
from grouppy.models import User
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash


@app.errorhandler(404)
def page_not_found(e):
    return render_template('_404.html'), 404


@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.log_in():
        return redirect(url_for('dashboard'))
    return render_template('login.html', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(
            form.password.data, method='sha256')
        new_user = User(username=form.username.data,
                        email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('signup.html', form=form)


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', name=current_user.username)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/profile/<string:username>')
def profile(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        return render_template('_404.html', message='User ' + username + " does not exist"), 404
    return render_template('profile.html', user=user)
