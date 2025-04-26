from flask_socketio import emit, send
from . import socketio
from monopoly.db import get_db
from monopoly.mainroom import get_room, get_rooms
from flask import Blueprint, g, session
from monopoly.rules import *


bp = Blueprint('events', __name__)

@socketio.on('message', namespace = '/private')
def handleMessage(data):
    rooms = get_rooms()
    data = {}
    for room in rooms:
        data[room['id']] = room['status']
    socketio.emit('message', data, broadcast=True, include_self=True, namespace = '/private')


@socketio.on('message', namespace = '/gaming')
def handleMessage(data):
    print('\n\n-----\n', data)
    map = Monopoly_map()
    data = Monopoly(data)
    socketio.emit('message', data, broadcast=True, include_self=True, namespace = '/gaming')
