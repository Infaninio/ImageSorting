"""A WebUi for ImageTinder to access a lokal nextcloud."""

from flask import Flask, redirect, render_template


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

    from . import auth

    app.register_blueprint(auth.bp)

    from . import configs

    app.register_blueprint(configs.bp)

    from . import images

    app.register_blueprint(images.bp)

    return app
