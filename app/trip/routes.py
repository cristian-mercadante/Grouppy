# -*- coding: utf8 -*-
from __future__ import division  # float division
from flask import render_template, url_for, redirect, request, flash, Blueprint
from forms import add_trip_form
from app.models import Friend, Trip
from flask_login import login_required, current_user
from datetime import datetime


trip = Blueprint('trip', __name__)


def get_trips(friend_id):
    trips = Trip.query(ancestor=current_user.key).fetch()
    trip_auto = []
    trip_pass = []
    for t in trips:
        if friend_id in t.autisti:
            trip_auto.append(t)
        elif friend_id in t.passeggeri:
            trip_pass.append(t)
    return trip_auto, trip_pass


def trip_error_redirection(form, message, style, trip_id, endpoint):
    flash(message, style)
    if not form:
        return redirect(url_for('user.dashboard'))
    return redirect(url_for(endpoint,
                            trip_id=trip_id,
                            titolo=form.titolo.data,
                            data=form.data.data,
                            partenza=form.partenza.data,
                            destinazione=form.destinazione.data,
                            distanza=form.distanza.data,
                            ritorno=form.ritorno.data,
                            pagato=form.pagato.data,
                            speciale=form.speciale.data
                            ))


def trip_get_handler(form, request, trip=None):
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
    if trip:
        for a in trip.autisti:
            label = 'auto' + str(a)
            if hasattr(form, label):
                getattr(form, label).data = 'y'
        for p in trip.passeggeri:
            label = 'pass' + str(p)
            if hasattr(form, label):
                getattr(form, label).data = 'y'


class Trip_POST_Handler():
    class_autisti = None
    class_passeggeri = None

    def __init__(self):
        self.class_autisti = None
        self.class_passeggeri = None

    def trip_post_handler(self, form, request, friends, trip_id, endpoint):
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
                    return trip_error_redirection(form, message, 'warning', trip_id, endpoint)
                else:
                    passeggeri.append(str(f.key.id()))
        if len(passeggeri) == 0:
            message = 'Non ci sono passeggeri.'
            return trip_error_redirection(form, message, 'warning', trip_id, endpoint)
        if len(autisti) == 0:
            message = 'Non ci sono autisti.'
            return trip_error_redirection(form, message, 'warning', trip_id, endpoint)
        if len(autisti) > len(passeggeri):
            message = u'Ci sono più autisti che passeggeri... Non dovrebbe succedere.'
            return trip_error_redirection(form, message, 'warning', trip_id, endpoint)
        self.class_autisti = autisti
        self.class_passeggeri = passeggeri


def get_auto_pass_scores(score, num_auto, num_pass):
    total = num_auto + num_pass
    score_passeggero = - score / total
    score_autista = score / num_auto + score_passeggero
    return score_autista, score_passeggero


def update_friends_score(score, form, autisti, passeggeri, trip_id, endpoint):
    persone = autisti + passeggeri
    score_autista, score_passeggero = get_auto_pass_scores(
        score, len(autisti), len(passeggeri))
    for p in persone:
        f = Friend.get_by_id(long(p), parent=current_user.key)
        if not f:
            continue
        if p in autisti:
            f.score += score_autista
        elif p in passeggeri:
            f.score += score_passeggero
        f.put()


def score_calc_total(num_auto, distanza, ritorno, pagato, speciale):
    score = float(distanza) * float(num_auto)
    if ritorno:
        score *= 2
    if pagato:
        score /= 10
    if speciale:
        score *= 1.1
    return score


@trip.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    friends = Friend.query(ancestor=current_user.key).fetch()
    if len(friends) < 2:
        message = u'Prima di aggiungere un\'uscita, è necessario aggiungere almeno 2 amici: aggiungine {}'.format(
            2 - len(friends))
        flash(message, 'warning')
        return redirect(url_for('friend.add'))
    form = add_trip_form(friends)
    if request.method == 'POST' and form.validate_on_submit():
        tph = Trip_POST_Handler()
        tph.trip_post_handler(form, request, friends, 0, 'trip.add')
        if tph.class_autisti and tph.class_passeggeri:
            # Aggironamento punteggi
            score = score_calc_total(len(tph.class_autisti),
                                     form.distanza.data,
                                     form.ritorno.data,
                                     form.pagato.data,
                                     form.speciale.data)
            update_friends_score(score, form, tph.class_autisti,
                                 tph.class_passeggeri, 0, 'trip.add')
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
                        autisti=map(long, tph.class_autisti),
                        passeggeri=map(long, tph.class_passeggeri),
                        score_total=score)
            trip.put()

            message = 'Uscita aggiunta con successo'
            flash(message, 'success')
            return redirect(url_for('user.dashboard'))
    elif request.method == 'GET':
        trip_get_handler(form, request)
    return render_template('trip.html', titolo='Aggiungi uscita', form=form, friends=friends, submit_to=url_for('trip.add'))


@trip.route('/edit/<trip_id>', methods=['GET', 'POST'])
@login_required
def edit(trip_id):
    trip = Trip.get_by_id(int(trip_id), parent=current_user.key)
    if not trip:
        return render_template('_404.html', message='Uscita non esistente'), 404
    friends = Friend.query(ancestor=current_user.key).fetch()
    form = add_trip_form(friends)
    if request.method == 'POST' and form.validate_on_submit():
        tph = Trip_POST_Handler()
        tph.trip_post_handler(form, request, friends,
                              trip_id, 'trip.edit')
        if tph.class_autisti and tph.class_passeggeri:
            new_score = score_calc_total(len(tph.class_autisti),
                                         form.distanza.data,
                                         form.ritorno.data,
                                         form.pagato.data,
                                         form.speciale.data)
            update_friends_score(-trip.score_total, form,
                                 trip.autisti, trip.passeggeri, trip_id, 'trip.edit')
            update_friends_score(
                new_score, form, tph.class_autisti, tph.class_passeggeri, trip_id, 'trip.edit')
            trip.titolo = form.titolo.data
            trip.data = form.data.data
            trip.partenza = form.partenza.data
            trip.destinazione = form.destinazione.data
            trip.distanza = form.distanza.data
            trip.ritorno = form.ritorno.data
            trip.pagato = form.pagato.data
            trip.speciale = form.speciale.data
            trip.autisti = map(long, tph.class_autisti)
            trip.passeggeri = map(long, tph.class_passeggeri)
            trip.score_total = new_score
            trip.put()

            message = 'Uscita modificata con successo'
            flash(message, 'success')
            return redirect(url_for('user.dashboard'))
    elif request.method == 'GET':
        trip_get_handler(form, request, trip)
    return render_template('trip.html', titolo='Modifica uscita', form=form, friends=friends,
                           submit_to=url_for('trip.edit', trip_id=trip_id))


@trip.route('/info/<trip_id>')
@login_required
def info(trip_id):
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


@trip.route('/delete/<trip_id>')
@login_required
def delete(trip_id):
    trip = Trip.get_by_id(int(trip_id), parent=current_user.key)
    if not trip:
        return render_template('_404.html', message='Uscita non esistente'), 404
    update_friends_score(-trip.score_total, None, trip.autisti,
                         trip.passeggeri, trip_id, url_for('trip.info', trip_id=trip_id))
    trip.key.delete()
    message = 'Uscita eliminata con successo'
    flash(message, 'success')
    return redirect(url_for('user.dashboard'))


@trip.route('/view')
@login_required
def view():
    trips = Trip.query(ancestor=current_user.key).fetch()
    return render_template('trip_view.html', trips=trips)
