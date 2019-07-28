# -*- coding: utf8 -*-
import os
import secrets
from PIL import Image
from flask import render_template, url_for, redirect, request, flash
from grouppy import app
from forms import LoginForm, RegisterForm, AddFriendForm, AddTripForm, UserSettingsForm, EditFriendForm
from models import User, Friend, Trip
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash

from google.appengine.ext import blobstore, ndb
from google.appengine.api import images
import werkzeug


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
    best_friends = friends[0:2]
    worst_friends = friends[-2:]
    return render_template('dashboard.html', user=current_user, friends=friends,
                           best_friends=best_friends, worst_friends=worst_friends)


@app.route('/add_friend', methods=['GET', 'POST'])
@login_required
def add_friend():
    form = AddFriendForm()
    if form.validate_on_submit():
        new_friend = Friend(email=form.email.data, nome=form.nome.data,
                            cognome=form.cognome.data, parent=current_user.key)
        new_friend.put()
        message = new_friend.nome + " " + new_friend.cognome + " aggiunto con successo!"
        flash(message, 'success')
        return redirect(url_for('dashboard'))
    return render_template('add_friend.html', form=form)


@app.route('/add_trip', methods=['GET', 'POST'])
@login_required
def add_trip():
    form = AddTripForm()
    if form.validate_on_submit():
        new_trip = Trip(titolo=form.titolo.data, data=form.data.data,
                        partenza=form.partenza.data, destinazione=form.destinazione.data,
                        distanza=form.distanza.data, parent=current_user.key)
        new_trip.put()
        return redirect(url_for('dashboard'))
    return render_template('add_trip.html', form=form)


@app.route('/user_settings', methods=['GET', 'POST'])
@login_required
def user_settings():
    form = UserSettingsForm()
    if form.validate_on_submit():
        current_user.email = form.email.data
        current_user.put()
        return redirect(url_for('dashboard'))
    elif request.method == 'GET':
        form.email.data = current_user.email
    return render_template('user_settings.html', form=form)


@app.route('/friend/<friend_id>')
@login_required
def friend_profile(friend_id):
    friend = Friend.get_by_id(int(friend_id), parent=current_user.key)
    if not friend:
        return render_template('_404.html', message='Amico non esistente'), 404
    return render_template('friend_profile.html', friend=friend)


@app.route('/friend/edit/<friend_id>', methods=['GET', 'POST'])
@login_required
def friend_edit(friend_id):
    friend = Friend.get_by_id(int(friend_id), parent=current_user.key)
    if not friend:
        return render_template('_404.html', message='Amico non esistente'), 404
    form = EditFriendForm()
    if request.method == 'POST' and form.validate_on_submit():
        friend.email = form.email.data
        friend.nome = form.nome.data
        friend.cognome = form.cognome.data

        uploaded_file = request.files.get('immagine')
        file_headers = uploaded_file.headers['Content-Type']
        blob_key = werkzeug.parse_options_header(file_headers)[1]['blob-key']
        image_url = images.get_serving_url(blob_key=blob_key)

        if friend.immagine_blob_key:
            blobstore.BlobInfo.get(friend.immagine_blob_key).delete()

        friend.immagine_url = image_url
        friend.immagine_blob_key = blobstore.BlobKey(blob_key)

        friend.put()
        message = friend.nome + " " + friend.cognome + " modificato con successo!"
        flash(message, 'success')
        return redirect(url_for('friend_profile', friend_id=friend_id))
    elif request.method == 'GET':
        form.email.data = friend.email
        form.nome.data = friend.nome
        form.cognome.data = friend.cognome
        upload_url = blobstore.create_upload_url(
            url_for('friend_edit', friend_id=friend_id))
    return render_template('friend_edit.html', friend=friend, form=form, upload_url=upload_url)


@app.route('/friend/delete/<friend_id>')
def friend_delete(friend_id):
    friend = Friend.get_by_id(int(friend_id), parent=current_user.key)
    if not friend:
        return render_template('_404.html', message='Amico non esistente'), 404
    message = friend.nome + " " + friend.cognome + " eliminato con successo!"
    if friend.immagine_blob_key:
        blobstore.BlobInfo.get(friend.immagine_blob_key).delete()
    friend.key.delete()
    flash(message, 'success')
    return redirect(url_for('dashboard'))
