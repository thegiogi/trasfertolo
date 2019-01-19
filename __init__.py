from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from waitress import serve
import os

app = Flask

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
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

    # register db functions
    from . import db
    db.init_app(app)
    #register authentication blueprint
    from . import auth
    app.register_blueprint(auth.bp)

    from . import travel
    app.register_blueprint(travel.bp)
    app.add_url_rule('/', endpoint='index')

    return app
