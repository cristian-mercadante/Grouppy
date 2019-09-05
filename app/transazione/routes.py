# -*- coding: utf8 -*-
from flask import render_template, url_for, redirect, request, flash, Blueprint
from forms import TransazioneForm
from app.models import Transazione
from flask_login import current_user, login_required


transazione = Blueprint('transazione', __name__)


@transazione.route('/add', methods=['GET', 'POST'])
@login_required
def add():
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
        return redirect(url_for('user.dashboard'))
    return render_template('transazione_form.html',
                           form=form,
                           titolo='Aggiungi transazione',
                           dest=url_for('transazione.add'))


@transazione.route('/edit/<transazione_id>', methods=['GET', 'POST'])
@login_required
def edit(transazione_id):
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
        return redirect(url_for('user.dashboard'))
    elif request.method == 'GET':
        form.titolo.data = transazione.titolo
        form.data.data = transazione.data
        form.costo.data = transazione.costo
        form.descrizione.data = transazione.descrizione
    return render_template('transazione_form.html',
                           form=form,
                           titolo='Modifica transazione',
                           dest=url_for('transazione.edit',
                                        transazione_id=transazione_id),
                           transazione=transazione)


@transazione.route('/delete/<transazione_id>')
@login_required
def delete(transazione_id):
    transazione = Transazione.get_by_id(
        int(transazione_id), parent=current_user.key)
    if not transazione:
        return render_template('_404.html', message='Transazione non esistente'), 404
    message = "Transazione eliminata con successo!"
    current_user.cassa -= transazione.costo
    current_user.put()
    transazione.key.delete()
    flash(message, 'success')
    return redirect(url_for('user.dashboard'))


@transazione.route('/view')
@login_required
def view():
    transazioni = Transazione.query(ancestor=current_user.key).fetch()
    return render_template('transazione_view.html', transazioni=transazioni)
