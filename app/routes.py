# -*- coding: utf8 -*-
from __future__ import division  # float division
from flask import render_template, url_for, redirect, request, flash
from grouppy import app
from forms import LoginForm, RegisterForm, AddFriendForm, UserSettingsForm, EditFriendForm, TransazioneForm
from forms import add_trip_form
from models import User, Friend, Trip, Transazione
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash
from datetime import datetime

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
    transazioni = Transazione.query(
        ancestor=current_user.key).order(-Transazione.data).fetch()
    uscite = Trip.query(
        ancestor=current_user.key).order(-Trip.data).fetch()
    return render_template('dashboard.html', user=current_user, friends=friends,
                           best_friends=best_friends, worst_friends=worst_friends,
                           transazioni=transazioni, uscite=uscite)


@app.route('/friend/add', methods=['GET', 'POST'])
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

        if form.immagine.data:
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


@app.route('/friend/pic_reset/<friend_id>')
def friend_pic_reset(friend_id):
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
    return redirect(url_for('friend_profile', friend_id=friend_id))


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


@app.route('/transazione/add', methods=['GET', 'POST'])
def add_transazione():
    form = TransazioneForm()
    if form.validate_on_submit():
        transazione = Transazione(titolo=form.titolo.data,
                                  descrizione=form.descrizione.data,
                                  data=form.data.data,
                                  costo=form.costo.data,
                                  parent=current_user.key)
        transazione.put()
        current_user.cassa = current_user.cassa + form.costo.data
        current_user.put()
        message = 'Transazione creata con successo!'
        flash(message, 'success')
        return redirect(url_for('dashboard'))
    return render_template('transazione_form.html',
                           form=form,
                           titolo='Aggiungi transazione',
                           dest=url_for('add_transazione'))


@app.route('/transazione/edit/<transazione_id>', methods=['GET', 'POST'])
def transazione_edit(transazione_id):
    transazione = Transazione.get_by_id(
        int(transazione_id), parent=current_user.key)
    if not transazione:
        return render_template('_404.html', message='Transazione non esistente'), 404
    form = TransazioneForm()
    if request.method == 'POST' and form.validate_on_submit():
        current_user.cassa = current_user.cassa - transazione.costo
        transazione.titolo = form.titolo.data
        transazione.data = form.data.data
        transazione.costo = form.costo.data
        transazione.descrizione = form.descrizione.data
        current_user.cassa = current_user.cassa + transazione.costo
        transazione.put()
        current_user.put()
        message = 'Transazione modificata con successo!'
        flash(message, 'success')
        return redirect(url_for('dashboard'))
    elif request.method == 'GET':
        form.titolo.data = transazione.titolo
        form.data.data = transazione.data
        form.costo.data = transazione.costo
        form.descrizione.data = transazione.descrizione
    return render_template('transazione_form.html',
                           form=form,
                           titolo='Modifica transazione',
                           dest=url_for('transazione_edit',
                                        transazione_id=transazione_id),
                           transazione=transazione)


@app.route('/transazione/delete/<transazione_id>')
def transazione_delete(transazione_id):
    transazione = Transazione.get_by_id(
        int(transazione_id), parent=current_user.key)
    if not transazione:
        return render_template('_404.html', message='Transazioen non esistente'), 404
    message = "Transazione eliminata con successo!"
    current_user.cassa -= transazione.costo
    current_user.put()
    transazione.key.delete()
    flash(message, 'success')
    return redirect(url_for('dashboard'))


def trip_error_redirection(form, message, style, endpoint):
    flash(message, style)
    return redirect(url_for(endpoint,
                        titolo=form.titolo.data,
                        data=form.data.data,
                        partenza=form.partenza.data,
                        destinazione=form.destinazione.data,
                        distanza=form.distanza.data,
                        ritorno=form.ritorno.data,
                        pagato=form.pagato.data,
                        speciale=form.speciale.data
                    ))

def trip_get_handler(form, request):
    form.titolo.data = request.args.get('titolo')
    if request.args.get('data'):
        form.data.data = datetime.strptime(
            request.args.get('data'), "%Y-%m-%d")
    form.partenza.data = request.args.get('partenza')
    form.destinazione.data = request.args.get('destinazione')
    form.distanza.data = request.args.get('distanza')
    if request.args.get('ritorno') == 'True':
        form.ritorno.data = 'y'
    if request.args.get('pagato') == 'True':
        form.pagato.data = 'y'
    if request.args.get('speciale') == 'True':
        form.speciale.data = 'y'

def trip_post_handler(form, request, friends, endpoint):
    autisti = []
    passeggeri = []
    for f in friends:
        fid_auto = 'auto' + str(f.key.id())
        fid_pass = 'pass' + str(f.key.id())
        auto = False
        if request.form.get(fid_auto):
            autisti.append(str(f.key.id()))
            auto = True
        if request.form.get(fid_pass):
            if auto:
                message = u'{} {} non può essere sia autista che passeggero.'.format(
                    f.nome, f.cognome)
                return trip_error_redirection(form, message, 'warning', endpoint)
            else:
                passeggeri.append(str(f.key.id()))
    if len(passeggeri) == 0:
        message = 'Non ci sono passeggeri.'
        return trip_error_redirection(form, message, 'warning', endpoint)
    if len(autisti) == 0:
        message = 'Non ci sono autisti.'
        return trip_error_redirection(form, message, 'warning', endpoint)
    if len(autisti) > len(passeggeri):
        message = u'Ci sono più autisti che passeggeri... Non dovrebbe succedere.'
        return trip_error_redirection(form, message, 'warning', endpoint)

    # Aggironamento punteggi
    score = score_calc_total(form.distanza.data,
                                form.ritorno.data,
                                form.pagato.data,
                                form.speciale.data)
    persone = autisti + passeggeri
    score_passeggero = - score / len(persone)
    score_autista = score / len(autisti) + score_passeggero
    for p in persone:
        f = Friend.get_by_id(long(p), parent=current_user.key)
        if not f:
            message = "Errore: id amico {} non esistente".format(a)
            return trip_error_redirection(form, message, 'danger', endpoint)
        if p in autisti:
            f.score += score_autista
        else:
            f.score += score_passeggero
        f.put()

    # SALVATAGGIO SU DATASTORE DELLA TRASFERTA
    trip = Trip(parent=current_user.key,
                titolo=form.titolo.data,
                data=form.data.data,
                partenza=form.partenza.data,
                destinazione=form.destinazione.data,
                distanza=form.distanza.data,
                ritorno=form.ritorno.data,
                pagato=form.pagato.data,
                speciale=form.speciale.data,
                autisti=map(long, autisti),
                passeggeri=map(long, passeggeri))
    trip.put()

    message = 'Uscita aggiunta con successo'
    flash(message, 'success')

@app.route('/uscita/add', methods=['GET', 'POST'])
@login_required
def add_trip():
    friends = Friend.query(ancestor=current_user.key).fetch()
    form = add_trip_form(friends)
    if request.method == 'POST' and form.validate_on_submit():
        trip_post_handler(form, request, friends, 'add_trip')
        return redirect(url_for('dashboard'))
    elif request.method == 'GET':
        trip_get_handler(form, request)
    return render_template('add_trip.html', form=form, friends=friends, submit_to=url_for('add_trip'))

@app.route('/uscita/edit/<trip_id>')
def edit_trip(trip_id):
    trip = Trip.get_by_id(int(trip_id), parent=current_user.key)
    if not trip:
        return render_template('_404.html', message='Uscita non esistente'), 404
    friends = Friend.query(ancestor=current_user.key).fetch()
    form = add_trip_form(friends)
    if request.method == 'POST' and form.validate_on_submit():

        trip_post_handler(form, request, friends, 'edit_trip')
        return redirect(url_for('dashboard'))
    elif request.method == 'GET':
        trip_get_handler(form, request)
    return render_template('add_trip.html', form=form, friends=friends, submit_to=url_for('edit_trip'))

def score_calc_total(distanza, ritorno, pagato, speciale):
    score = float(distanza)
    if ritorno:
        score *= 2
    if pagato:
        score /= 10
    if speciale:
        score *= 1.1
    return score


@app.route('/reset_scores')
def reset_scores():
    friends = Friend.query(ancestor=current_user.key).fetch()
    for f in friends:
        f.score = 0
        f.put()
    return 'ok'


@app.route('/uscita/<trip_id>')
def trip_info(trip_id):
    trip = Trip.get_by_id(int(trip_id), parent=current_user.key)
    if not trip:
        return render_template('_404.html', message='Uscita non esistente'), 404
    autisti = []
    for a in trip.autisti:
        f = Friend.get_by_id(a, parent=current_user.key)
        autisti.append(f)
    passeggeri = []
    for p in trip.passeggeri:
        f = Friend.get_by_id(p, parent=current_user.key)
        passeggeri.append(f)
    return render_template('trip_info.html', trip=trip, autisti=autisti, passeggeri=passeggeri)




# GOOGLE MAPS API INTEGRATION
@app.route('/map_test')
def map_test():
    return render_template('map_test.html')
