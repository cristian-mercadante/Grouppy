# -*- coding: utf8 -*-
from __future__ import division  # float division
from flask import render_template, url_for, redirect, request, flash, Blueprint
from forms import AddFriendForm, EditFriendForm
from app.models import Friend
from flask_login import login_required, current_user
from app.trip.routes import get_trips, get_auto_pass_scores

from google.appengine.ext import blobstore
from google.appengine.api import images
import werkzeug


friend = Blueprint('friend', __name__)


@friend.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    form = AddFriendForm()
    if form.validate_on_submit():
        new_friend = Friend(email=form.email.data, nome=form.nome.data,
                            cognome=form.cognome.data, parent=current_user.key)
        new_friend.put()
        message = new_friend.nome + " " + new_friend.cognome + " aggiunto con successo!"
        flash(message, 'success')
        return redirect(url_for('user.dashboard'))
    return render_template('friend_add.html', form=form)


@friend.route('/profile/<friend_id>')
@login_required
def profile(friend_id):
    friend = Friend.get_by_id(int(friend_id), parent=current_user.key)
    if not friend:
        return render_template('_404.html', message='Amico non esistente'), 404
    trip_auto, trip_pass = get_trips(int(friend_id))
    return render_template('friend_profile.html', friend=friend, trip_auto=trip_auto, trip_pass=trip_pass, score_func=get_auto_pass_scores)


@friend.route('/edit/<friend_id>', methods=['GET', 'POST'])
@login_required
def edit(friend_id):
    friend = Friend.get_by_id(int(friend_id), parent=current_user.key)
    if not friend:
        return render_template('_404.html', message='Amico non esistente'), 404
    form = EditFriendForm()
    upload_url = blobstore.create_upload_url(
        url_for('friend.edit', friend_id=friend_id))
    if request.method == 'POST' and form.validate_on_submit():
        friend.email = form.email.data
        friend.nome = form.nome.data
        friend.cognome = form.cognome.data

        if form.immagine.data:
            uploaded_file = request.files.get('immagine')
            file_headers = uploaded_file.headers['Content-Type']
            blob_key = werkzeug.parse_options_header(file_headers)[
                1]['blob-key']
            image_url = images.get_serving_url(blob_key=blob_key)

            if friend.immagine_blob_key:
                blobstore.BlobInfo.get(friend.immagine_blob_key).delete()

            friend.immagine_url = image_url
            friend.immagine_blob_key = blobstore.BlobKey(blob_key)

        friend.put()
        message = friend.nome + " " + friend.cognome + " modificato con successo!"
        flash(message, 'success')
        return redirect(url_for('friend.profile', friend_id=friend_id))
    elif request.method == 'GET':
        form.email.data = friend.email
        form.nome.data = friend.nome
        form.cognome.data = friend.cognome
    return render_template('friend_edit.html', friend=friend, form=form, upload_url=upload_url)


@friend.route('/pic_reset/<friend_id>')
@login_required
def pic_reset(friend_id):
    friend = Friend.get_by_id(int(friend_id), parent=current_user.key)
    if not friend:
        return render_template('_404.html', message='Amico non esistente'), 404
    if friend.immagine_blob_key:
        blobstore.BlobInfo.get(friend.immagine_blob_key).delete()
        friend.immagine_blob_key = None
        friend.immagine_url = None
        friend.put()
    message = 'Immagine eliminata con successo!'
    flash(message, 'success')
    return redirect(url_for('friend.profile', friend_id=friend_id))


@friend.route('/delete/<friend_id>')
@login_required
def delete(friend_id):
    friend = Friend.get_by_id(int(friend_id), parent=current_user.key)
    if not friend:
        return render_template('_404.html', message='Amico non esistente'), 404
    message = friend.nome + " " + friend.cognome + " eliminato con successo!"
    if friend.immagine_blob_key:
        blobstore.BlobInfo.get(friend.immagine_blob_key).delete()
    friend.key.delete()
    flash(message, 'success')
    return redirect(url_for('user.dashboard'))
