import random

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from monopoly.mainroom import get_room, get_user
from monopoly.auth import login_required
from monopoly.db import get_db

from .rules import *


bp = Blueprint('game', __name__)
@login_required
@bp.route('/<int:id>')
def game(id):
    db = get_db()
    room = get_room(id, False)
    players=[]
    #!!!!!!!!!!!!!!!!!!!!!!!!!
    for i in list(room['players_list'].split(',')):
        player = get_user(int(i))
        players.append(player)
    map = Monopoly_map()
    cells = map.get_map()
    return render_template('game/game.html', room=room, players=players, cells=cells)
