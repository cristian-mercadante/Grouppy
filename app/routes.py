# -*- coding: utf8 -*-
from flask import render_template, url_for, redirect, request
from grouppy import app
from forms import LoginForm, RegisterForm, AddFriendForm, AddTripForm, UserSettingsForm
from models import User, Friend, Trip
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash


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
        new_user = User(id=form.username.data, username=form.username.data,
                        email=form.email.data, password=hashed_password)
        new_user.put()
        return redirect(url_for('login'))
    return render_template('signup.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/dashboard')
@login_required
def dashboard():
    friends = Friend.query(
        ancestor=current_user.key).order(-Friend.score).fetch()
    best_friends = friends[0:4]
    return render_template('dashboard.html', user=current_user, friends=friends, best_friends=best_friends)


@app.route('/add_friend', methods=['GET', 'POST'])
@login_required
def add_friend():
    form = AddFriendForm()
    if form.validate_on_submit():
        new_friend = Friend(id=form.email.data, email=form.email.data, nome=form.nome.data,
                            cognome=form.cognome.data, parent=current_user.key)
        new_friend.put()
        return redirect(url_for('dashboard'))
    return render_template('add_friend.html', form=form)


@app.route('/add_trip', methods=['GET', 'POST'])
@login_required
def add_trip():
    form = AddTripForm()
    if form.validate_on_submit():
        new_trip = Trip(id=form.email.data, email=form.email.data, nome=form.nome.data,
                        cognome=form.cognome.data, parent=current_user.key)
        new_trip.put()
        return redirect(url_for('dashboard'))
    return render_template('add_trip.html', form=form)


@app.route('/user_settings', methods=['GET', 'POST'])
def user_settings():
    form = UserSettingsForm()
    if form.validate_on_submit():
        current_user.email = form.email.data
        current_user.put()
        return redirect(url_for('dashboard'))
    elif request.method == 'GET':
        form.email.data = current_user.email
    return render_template('user_settings.html', form=form)
