from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from werkzeug.security import check_password_hash, generate_password_hash

from monopoly.auth import login_required
from monopoly.db import get_db

bp = Blueprint('profile', __name__, url_prefix='/profile')

def get_user(id):
    db = get_db()
    user = db().execute(
    'SELECT *'
    ' FROM user'
    ' WHERE user.id = ?',
    (id,)
    ).fetchone()
    return user

@bp.route('/')
@login_required
def profile(id):
    user = get_user(id)
    return render_template('profile/profile.html', user=user)

@bp.route('/<int:id>/edit', methods=('GET', 'POST'))
@login_required
def edit(id):
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_confirm = request.form['password_confirm']
        error = None

        if not password_confirm:
            error = 'Confirm password'
        elif password_confirm != password:
            error = 'Passwords must match'

        if error is None:
            try:
                db = get_db()
                db.execute(
                    'UPDATE user'
                    ' SET username=?, password=?'
                    ' WHERE id = ?',
                    (username, generate_password_hash(password), id)
                )
                db.commit()
            except db.IntegrityError:
                error = f"Password {password} is bad."
            else:
                return redirect(url_for('profile'))

        flash(error)

    return render_template('profile/edit.html')
