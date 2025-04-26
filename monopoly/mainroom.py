from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort
from flask_socketio import SocketIO, emit, send
from monopoly.auth import login_required
from monopoly.db import get_db

def get_user(id):
    db = get_db()
    user = db.execute(
        'SELECT username'
        ' FROM user u'
        ' WHERE u.id=?',
        (id,)
    ).fetchone()
    try:
        return user['username']
    except:
        return


def get_status(id):
    db = get_db()
    status = db.execute(
        'SELECT status'
        ' FROM room r'
        ' WHERE r.id = ?',
        (id,)
    ).fetchone()


def get_rooms():
    db = get_db()
    rooms = db.execute(
        'SELECT r.id, title, created, players_list, status, author_id, username'
        ' FROM room r JOIN user u ON r.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return rooms

bp = Blueprint('mainroom', __name__)

@bp.route('/')
def index():
    db = get_db()
    rooms = get_rooms()
    players = []
    for room in rooms:
        if room['players_list'] is not None:
            players.append(list(map(get_user, room['players_list'].split(','))))
        else: players.append([])
    return render_template('mainroom/index.html', rooms=rooms, players=players)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO room (title, author_id)'
                ' VALUES (?, ?)',
                (title, g.user['id'])
            )
            db.commit()
            return redirect(url_for('mainroom.index'))

    return render_template('mainroom/create.html')

def get_room(id, check_author=True):
    room = get_db().execute(
        'SELECT r.id, title, created, author_id, players_list, status'
        ' FROM room r JOIN user u ON r.author_id = u.id'
        ' WHERE r.id = ?',
        (id,)
    ).fetchone()

    if room is None:
        abort(404, f"Room id {id} doesn't exist.")

    if check_author and room['author_id'] != g.user['id']:
        abort(403)

    return room

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    room = get_room(id)

    if request.method == 'POST':
        title = request.form['title']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE room SET title = ?'
                ' WHERE id = ?',
                (title, id)
            )
            db.commit()

            return redirect(url_for('mainroom.index'))
    if room['players_list'] is not None:
        players = list(map(get_user, room['players_list'].split(',')))
    else: players = []

    return render_template('mainroom/update.html', room=room, players=players)

@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    get_room(id)
    db = get_db()
    db.execute('DELETE FROM room WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('mainroom.index'))


@bp.route('/<int:id>/room', methods=['GET', 'POST'])
@login_required
def go_to_room(id):
    db=get_db()
    rooms = get_rooms()
    room = get_room(id, False)
    ids=[]
    if room['players_list'] is not None:
        players = list(map(get_user, room['players_list'].split(',')))
        ids = room['players_list'].split(',')
        if str(g.user['id']) in ids:
            player_ready = bool(int(room['status'][ids.index(str(g.user['id']))]))
        else: player_ready = False
    else:
        player_ready = False
        players = []
    return render_template('mainroom/room.html', room=room, players=players, player_ready=player_ready, ids=ids, rooms = rooms)


@bp.route('/<int:id>/room/leave', methods=['POST'])
@login_required
def leave_room(id):
    if request.method == 'POST':
        room = get_room(id, False)
        players = str(room['players_list'])
        players = players.split(sep=',')
        status = str(room["status"])
        if str(g.user['id']) in players:
            if len(players) == 1:
                status = None
            else:
                i = players.index(str(g.user['id']))
                status = status[:i] +  status[i+1:]
            players.remove(str(g.user['id']))
            players=','.join(players)
            if players == '':
                players = None
            db = get_db()
            db.execute(
                'UPDATE room SET players_list = ?, status = ?'
                ' WHERE id = ?',
                (players, status, id)
            )
            db.commit()
        return redirect(url_for('mainroom.index'))


@bp.route('/<int:id>/room/join', methods=['POST'])
@login_required
def join_room(id):
    room = get_room(id, False)
    if request.method == 'POST':
        if room['players_list'] is None:
            players=str(g.user['id'])
            status = '0'
        else:
            players = room['players_list']
            status = room['status']
        players = players.split(sep=',')
        if str(g.user['id']) not in players:
            players.append(str(g.user['id']))
            if len(players) == 1 or None in players or '' in players:
                status='0'
            else:
                status+='0'
        players=','.join(players)
        db = get_db()
        if status[0]=='' or status[0]==None:
            status.pop(0)
        db.execute(
            'UPDATE room SET players_list = ?, status = ?'
            ' WHERE id = ?',
            (players, status, id)
        )
        db.commit()
    return redirect(url_for('.go_to_room', id=room['id']))
@bp.route('/<int:id>/room/<int:player_ready>/ready', methods=['POST'])
@login_required
def ready(id, player_ready):
    room = get_room(id, False)
    if request.method == 'POST':
        if room['players_list'] is not None:
            players = room['players_list']
            players = players.split(sep=',')
            i = players.index(str(g.user["id"]))
            status = room['status']
            if player_ready: ready_index = '1'
            else: ready_index = '0'
            status = status[:i] + ready_index + status[i+1:]
            db = get_db()
            db.execute(
                'UPDATE room SET status = ?'
                ' WHERE id = ?',
                (status, id)
            )
            db.commit()
    return redirect(url_for('.go_to_room', id=room['id']))
