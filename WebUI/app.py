"""A WebUi for ImageTinder to access a lokal nextcloud."""

import logging
import os

from dotenv import load_dotenv
from flask import Flask, redirect, render_template
from flask_executor import Executor
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from .scheduler import get_scheduler

load_dotenv(override=True)

if os.environ.get("IMAGE_SORT_DEBUG", False) == "True":
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.WARNING)

executor = Executor()


def create_app(test_config=None) -> Flask:
    """Create the ImageTinder Webbapp.

    Parameters
    ----------
    test_config : _type_, optional
        Configuration for testing, by default None

    Returns
    -------
    Flask
        A Flask app.
    """
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",  # pragma: allowlist secret
    )

    app.config["EXECUTOR_MAX_WORKERS"] = 5
    executor.init_app(app)
    limiter = Limiter(get_remote_address, default_limits=["1/second"])
    limiter.init_app(app)

    # a simple page that says hello

    @app.route("/")
    def root():
        return redirect("/index")

    @app.route("/index")
    def index():
        return render_template("welcome.html")

    @app.route("/noAdmin")
    def noAdmin():
        return render_template("noAdmin.html")

    from . import auth, configs, images

    limiter.limit("4/minute")(auth.bp)
    limiter.exempt(images.bp)

    app.register_blueprint(configs.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(images.bp)

    scheduler = get_scheduler()
    scheduler.start()

    return app
