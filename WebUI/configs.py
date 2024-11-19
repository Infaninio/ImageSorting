from flask import Blueprint, redirect, render_template, session

from .database import get_db

bp = Blueprint("configs", __name__, url_prefix="/configs")


@bp.route("/overview", methods=("GET", "POST"))
def overview():
    """Overviewpage of the configurations."""
    collections = []
    db = get_db()
    if "user_id" not in session:
        return redirect("/auth/login")
    collections = db.get_user_collections(user_id=session["user_id"])
    collections = [col.dict for col in collections]

    return render_template(
        "configs/overview.html",
        configs=collections,
    )
