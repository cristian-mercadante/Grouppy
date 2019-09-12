# -*- coding: utf8 -*-
from flask import render_template, url_for, redirect, request, Blueprint
from forms import LoginForm, RegisterForm, UserSettingsForm
from app.models import User, Friend, Trip, Transazione
from flask_login import login_required, logout_user, current_user
from werkzeug.security import generate_password_hash


user = Blueprint('user', __name__)


@user.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('user.dashboard'))
    return render_template('index.html')


@user.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('user.dashboard'))
    form = LoginForm()
    if form.log_in():
        return redirect(url_for('user.dashboard'))
    return render_template('login.html', form=form)


@user.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('user.dashboard'))
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(
            form.password.data, method='sha256')
        new_user = User(id=form.username.data, username=form.username.data,
                        email=form.email.data, password=hashed_password)
        new_user.put()
        return redirect(url_for('user.login'))
    return render_template('signup.html', form=form)


@user.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('user.index'))


@user.route('/dashboard')
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


@user.route('/dashboard/<username>')
def dashboard_nologin(username):
    user = User.get_by_id(username)
    if not user:
        return render_template('_404.html', message='Utente non esistente'), 404
    friends = Friend.query(ancestor=user.key).order(-Friend.score).fetch()
    best_friends = friends[0:2]
    worst_friends = friends[-2:]
    transazioni = Transazione.query(
        ancestor=user.key).order(-Transazione.data).fetch(10)
    uscite = Trip.query(ancestor=user.key).order(-Trip.data).fetch(10)
    return render_template('dashboard.html', user=user, friends=friends,
                           best_friends=best_friends, worst_friends=worst_friends,
                           transazioni=transazioni, uscite=uscite)


@user.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    form = UserSettingsForm()
    if form.validate_on_submit():
        current_user.email = form.email.data
        current_user.put()
        return redirect(url_for('user.dashboard'))
    elif request.method == 'GET':
        form.email.data = current_user.email
    return render_template('user_settings.html', form=form)


# GOOGLE MAPS API INTEGRATION
'''
@user.route('/map_test')
def map_test():
    return render_template('map_test.html')
'''
