import os.path
import sys
from datetime import timedelta

from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager

import webapp.db.accounting_functions as db_ac
from webapp.db.db_functions import init_app
from webapp.routes.accounting import accounting_bp
from webapp.routes.courses import courses_bp
import webapp.exceptions.exceptions as exceptions


def create_app(config: dict = None):
    app = Flask("podcast-website")
    app.config.from_mapping(
        DATABASE=os.path.join(os.getcwd(), os.getenv("DATABASE", "database.db")),
        AUTH_SALT=os.getenv("AUTH_SALT"),
        SECRET_KEY=os.getenv("SECRET_KEY"),
        PERMANENT_SESSION_LIFETIME=timedelta(seconds=int(os.getenv('PERMANENT_SESSION_LIFETIME', 604800)))
    )
    app.jinja_env.filters['zip'] = zip

    if os.getenv("TEST") == "false":
        if os.getenv("AUTH_SALT") is None or os.getenv("FLASK_RUN_PORT") is None or os.getenv("SECRET_KEY") is None:
            sys.exit("!!!!!!\nProgram needs a specified web_port/salt/secret in settings\n!!!!!!")

    if config is not None:
        app.config.update(config)
    init_app(app)
    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id: str):
        return db_ac.find_user_by_id(user_id)

    @app.errorhandler(404)
    def not_found(e: exceptions):
        return render_template("404.html")

    @login_manager.unauthorized_handler
    def unauthorized():
        return render_template('403.html'), 403

    @app.route("/")
    def index():
        return redirect(url_for("courses.show_courses"))

    app.register_blueprint(accounting_bp)

    app.register_blueprint(courses_bp, url_prefix="/courses")

    return app
