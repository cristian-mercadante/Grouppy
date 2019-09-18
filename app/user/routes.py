# -*- coding: utf8 -*-
from flask import render_template, url_for, redirect, request, Blueprint, flash
from forms import (LoginForm, RegisterForm, ChangeEmailForm,
                   ChangePasswordForm, ResetPasswordForm, ResetPasswordRequestForm)
from app.models import User, Friend, Trip, Transazione
from flask_login import login_required, logout_user, current_user
from werkzeug.security import generate_password_hash
from google.appengine.api import mail
from google.appengine.runtime import apiproxy_errors
import logging


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
    return render_template('user_login.html', form=form)


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
    return render_template('user_signup.html', form=form)


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
    form = ChangeEmailForm()
    if form.validate_on_submit():
        current_user.email = form.email.data
        current_user.put()
        message = 'Email cambiata con successo'
        flash(message, 'success')
        return redirect(url_for('user.dashboard'))
    elif request.method == 'GET':
        form.email.data = current_user.email
    return render_template('user_settings.html', form=form)


@user.route('/settings/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(
            form.new_password.data, method='sha256')
        current_user.password = hashed_password
        current_user.put()
        message = 'Password cambiata con successo'
        flash(message, 'success')
        return redirect(url_for('user.dashboard'))
    return render_template('user_change_password.html', form=form)


def send_reset_email(user):
    email = user.email
    token = user.get_reset_token()
    sender = 'noreply@grouppy.appspotmail.com'
    to = "{} <{}>".format(user.username, user.email)
    subject = "Grouppy Password Reset"
    body = """
Ciao {}
Per resettare la password, clicca sul link:
{}

Se non hai richiesto il reset della password, ignora questa mail.

Grouppy
""".format(user.username, url_for('user.reset_token', token=token, _external=True))

    try:
        mail.send_mail(sender=sender, to=to, subject=subject, body=body)
    except apiproxy_errors.OverQuotaError, msg:
        logging.error(msg)
        message = u'Impossibile inviare mail. Riprova più tardi'
        flash(message, 'danger')
        return redirect(url_for('user.login'))
    message = u'È stata inviata una mail per il reset della password'
    flash(message, 'success')


@user.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('user.dashboard'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.get_by_id(form.username.data)
        send_reset_email(user)
        return redirect(url_for('user.login'))
    return render_template('user_reset_request.html', form=form)


@user.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('user.dashboard'))
    user = User.verify_reset_token(token)
    if not user:
        message = 'Link non valido, tempo scaduto'
        flash(message, 'warning')
        return redirect(url_for('user.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(
            form.password.data, method='sha256')
        user.password = hashed_password
        user.put()
        message = 'Password cambiata con successo. Eseguire il login'
        flash(message, 'success')
        return redirect(url_for('user.login'))
    return render_template('user_reset_token.html', form=form, token=token)


@user.route('/about')
def about():
    return render_template('about.html')


# GOOGLE MAPS API INTEGRATION
'''
@user.route('/map_test')
def map_test():
    return render_template('map_test.html')
'''
