from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from trasfertolo.auth import login_required
from trasfertolo.db import get_db

bp = Blueprint('travel', __name__)

@bp.route('/')
@login_required
def index():
    db = get_db()
    travels = db.execute(
        'SELECT t.id, destination, traveldate, body, created, author_id, username, will_drive'
        ' FROM travels t JOIN user u ON t.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('travel/index.html', travels = travels)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['destination']
        body = request.form['body']
        tdate = request.form['tdate']
        ttime = request.form['ttime']
        traveldate = tdate + " " + ttime + ":00"
        print(traveldate)
        error = None

        if not title:
            error = 'Destination is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO travels (destination, body, author_id, traveldate)'
                ' VALUES (?, ?, ?, ?)',
                (title, body, g.user['id'], traveldate)
            )
            db.commit()
            return redirect(url_for('travel.index'))

    return render_template('travel/create.html')

def get_post(id, check_author=True):
    travel = get_db().execute(
        'SELECT p.id, destination, body, date(traveldate) as traveldate, time(traveldate) as traveltime, created, author_id, username'
        ' FROM travels p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if travel is None:
        abort(404, "travel id {0} doesn't exist.".format(id))

    if check_author and travel['author_id'] != g.user['id']:
        abort(403)


    return travel

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    travel = get_post(id)
    
    if request.method == 'POST':
        title = request.form['destination']
        body = request.form['body']
        traveldate = request.form['tdate']
        traveltime = request.form['ttime']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE travels SET destination = ?, body = ?, traveldate = ?'
                ' WHERE id = ?',
                (title, body, traveldate + " " + traveltime + ":00", id)
            )
            db.commit()
            return redirect(url_for('travel.index'))
    print(type(travel["traveldate"]))
    return render_template('travel/update.html', travel=travel)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM travels WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('travel.index'))
