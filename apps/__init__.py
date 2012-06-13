#!/usr/bin/env python

import os
import os.path
from logging import getLogger

from flask import Flask, g, redirect, render_template, request, url_for

from flask_debugtoolbar import DebugToolbarExtension
from flask.ext.admin.contrib.fileadmin import FileAdmin

from flask.ext.assets import Environment, Bundle

from flask.ext.login import LoginManager
from flaskext.principal import Principal, RoleNeed, UserNeed, identity_loaded

from logbook.compat import RedirectLoggingHandler

from extensions import admin, babel, bcrypt, cache, mail


def configure_app(app, filename):
    """ Load the app's configuration. """

    app.config.from_pyfile(filename)

def configure_admin(app):

    admin.add_view(FileAdmin(app.config['STATIC_ROOT'], '/static/', name='Static Files'))
    #admin.add_view(ModelView(User, sqldb.session))
    admin.init_app(app) 

def configure_assets(app):
    """ Set up Flask-Assets """

    assets = Environment(app)
    assets_output_dir = os.path.join(app.config['STATIC_ROOT'], 'gen')
    if not os.path.exists(assets_output_dir):
        os.mkdir(assets_output_dir)

   
    less_css = Bundle('less/style.less',
                filters='less',
                output='gen/style.css',
                debug=False
                )

    coffee_script = Bundle('coffee/script.coffee',
            filters='coffeescript',
            output='gen/script.js',
            debug=False
            )
            

    assets.register('css_all', less_css,
            filters='cssmin',
            output='gen/packed.css',
            debug=app.debug
            )

    assets.register('js_all', 'js/plugins.js', coffee_script,
            filters='uglifyjs',
            output='gen/packed.js',
            debug=app.debug)
    
def configure_before_handlers(app):
    pass
    """
    @app.before_request
    def authenticate():
        g.user = getattr(g.identity, 'user', None)
    """

def configure_blueprints(app):

    # Front-end
    from frontend import frontend
    app.register_blueprint(frontend)

    # Users
    #from users import users
    #app.register_blueprint(users)
    # profiles
    #from profiles import profiles
    #from profiles.models import Profile
    #app.register_blueprint(profiles)
    #db.register([Profile])

    # listings
    from listings import listings
    app.register_blueprint(listings, url_prefix='/listings')
    #from listings.models import Route, Shelter, Transport, Listing
    #mongodb.register([Listing, Transport, Shelter, Route])


def configure_errorhandlers(app):

    @app.errorhandler(401)
    def unauthorized(error):
        return redirect(url_for('users.login', next=request.path))

    @app.errorhandler(403)
    def forbidden(error):
        return render_template('error/403.html', error=error)

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('error/404.html', error=error)

    @app.errorhandler(500)
    def server_error(error):
        return render_template('error/500.html', error=error)


def configure_extensions(app):

    configure_assets(app)
    bcrypt.init_app(app)
    babel.init_app(app)
    cache.init_app(app)
    celery = Celery(app)
    mail.init_app(app)
    mongodb.init_app(app)
    sqldb.init_app(app)

    if app.debug:
        debugtoolbar = DebugToolbarExtension(app)

def configure_identity(app):
    
    pass
    """
    login_manager = LoginManager()
    login_manager.setup_app(app)

    login_manager.login_view = 'apps.users.login'
    login_manager.login_message = 'Please log in to access this page.'

    @login_manager.user_loader
    def load_user(userid):
        return User.get(userid)

    #@login_manager.token_loader
    #def load_token(user_token):
    #    return User.get_auth_token(user_token) 

    principal = Principal(app)

    @identity_loaded.connect_via(app)
    def on_identity_loaded(sender, identity):
        g.user = User.query_from_identity(identity)

    """

def configure_il8n(app):
    """ Configure internationalization with Flask-Babel. """
    @babel.localeselector
    def get_locale():
        accept_languages = app.config.get('ACCEPT_LANGUAGES', ['en'])
        return request.accept_languages.best_match(accept_languages)


def configure_logging(app):
    """ Setup the app's loggers. We use logbook so we need to redirect all
    app.logger calls to logbook using the RedirectLoggingHandler
    """
    loggers = [
            getLogger(app.config['LOGGER_NAME']),
            getLogger('sqlalchemy'), 
            getLogger('mongokit')
            ]

    for l in loggers:
        l.addHandler(RedirectLoggingHandler())
    

def configure_template_filters(app):
    pass


def generate_app(config):

    app = Flask(__name__)
    
    configure_app(app, config)
    configure_logging(app)
    configure_extensions(app)
    configure_identity(app)
    configure_admin(app)
    configure_before_handlers(app)
    configure_errorhandlers(app)
    configure_blueprints(app)
    configure_assets(app)
    configure_template_filters(app)

    return app
