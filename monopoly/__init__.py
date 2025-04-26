import os
from flask import request, Flask, render_template
from monopoly.mainroom import get_room
from monopoly.db import get_db
from flask_socketio import SocketIO
from werkzeug.middleware.proxy_fix import ProxyFix

socketio = SocketIO() #async_mode='eventlet'


def create_app(debug=False, test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.debug = debug
    app.config['SECRET_KEY'] = 'brother'
    socketio.init_app(app)

    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    app.wsgi_app = ProxyFix(app.wsgi_app)

    @app.route('/profile', methods=["GET"])
    def index():
        return render_template('profile/profile.html')

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('error/page_not_found.html'), 404

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import mainroom
    app.register_blueprint(mainroom.bp)
    app.add_url_rule('/', endpoint='index')

    from . import profile
    app.register_blueprint(profile.bp)
    app.add_url_rule('/profile', endpoint='profile')

    from . import game
    app.register_blueprint(game.bp)
    app.add_url_rule('/game', endpoint='game')

    from . import events
    app.register_blueprint(events.bp)

    return app
