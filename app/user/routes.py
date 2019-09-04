# -*- coding: utf8 -*-
from flask import render_template, url_for, redirect, request, Blueprint
from forms import LoginForm, RegisterForm, UserSettingsForm
from app.models import User, Friend, Trip, Transazione
from flask_login import login_required, logout_user, current_user
from werkzeug.security import generate_password_hash


user_bp = Blueprint('user_bp', __name__)


@user_bp.errorhandler(404)
def page_not_found(e):
    return render_template('_404.html'), 404


@user_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('user_bp.dashboard'))
    return render_template('index.html')


@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('user_bp.dashboard'))
    form = LoginForm()
    if form.log_in():
        return redirect(url_for('user_bp.dashboard'))
    return render_template('login.html', form=form)


@user_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('user_bp.dashboard'))
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(
            form.password.data, method='sha256')
        new_user = User(id=form.username.data, username=form.username.data,
                        email=form.email.data, password=hashed_password)
        new_user.put()
        return redirect(url_for('user_bp.login'))
    return render_template('signup.html', form=form)


@user_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('user_bp.index'))


@user_bp.route('/dashboard')
@login_required
def dashboard():
    friends = Friend.query(
        ancestor=current_user.key).order(-Friend.score).fetch()
    best_friends = friends[0:2]
    worst_friends = friends[-2:]
    transazioni = Transazione.query(
        ancestor=current_user.key).order(-Transazione.data).fetch(10)
    uscite = Trip.query(
        ancestor=current_user.key).order(-Trip.data).fetch(10)
    return render_template('dashboard.html', user=current_user, friends=friends,
                           best_friends=best_friends, worst_friends=worst_friends,
                           transazioni=transazioni, uscite=uscite)


@user_bp.route('/user_settings', methods=['GET', 'POST'])
@login_required
def user_settings():
    form = UserSettingsForm()
    if form.validate_on_submit():
        current_user.email = form.email.data
        current_user.put()
        return redirect(url_for('user_bp.dashboard'))
    elif request.method == 'GET':
        form.email.data = current_user.email
    return render_template('user_settings.html', form=form)


# GOOGLE MAPS API INTEGRATION
'''
@user_bp.route('/map_test')
def map_test():
    return render_template('map_test.html')
'''
