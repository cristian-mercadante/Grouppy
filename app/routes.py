# -*- coding: utf8 -*-
from flask import render_template, url_for, redirect
from grouppy import app
from forms import LoginForm, RegisterForm
from models import User
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
    return render_template('dashboard.html', user=current_user)
