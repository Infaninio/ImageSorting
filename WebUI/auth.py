import functools
import logging
from uuid import uuid4

from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from .database import db_wrapper

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/register", methods=("GET", "POST"))
def register():
    """Webpage for registering a new User."""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        db = db_wrapper.ImageTinderDatabase()
        error = None

        if not username:
            error = "Username is required."
        elif not password:
            error = "Password is required."

        if error is None:
            try:
                db.create_user(username=username, password=password)
            except db_wrapper.UserAlreadyExists:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template("auth/register.html")


@bp.route("/login", methods=("GET", "POST"))
def login():
    """Webpage for UserLogin."""
    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        db = db_wrapper.ImageTinderDatabase()

        try:
            user = db.get_user_id_from_table(username=username, password=password)
        except db_wrapper.UserNotExisting:
            error = "User does not exist. Try another username or register."
            logging.warning(f"Can't find user {username}")
        except db_wrapper.WrongPassword:
            error = "Your Password was wrong, try again."
            logging.warning(f"Password wrong for {username}")

        if error is None:
            session.clear()
            session["user_id"] = user
            session["uuid"] = str(uuid4())
            return redirect(url_for("configs.overview"))

        flash(error)

    return render_template("auth/login.html", error_message=error)


@bp.before_app_request
def load_logged_in_user():
    """Get the currently logged in user."""
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        g.user = db_wrapper.get_db().get_username(user_id)


@bp.route("/logout")
def logout():
    """Logout the user."""
    session.clear()
    return redirect(url_for("index"))


def login_required(view):
    """When login required redirect to login."""

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))

        return view(**kwargs)

    return wrapped_view
