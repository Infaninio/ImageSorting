import base64
import io
from datetime import datetime

import matplotlib.pyplot as plt
from flask import Blueprint, redirect, render_template, request, session, url_for

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


@bp.route("/<config_id>", methods=("GET", "POST"))
def show_config(config_id: str):
    """Display the overview of a specific configuration."""
    db = get_db()
    if request.method == "POST":
        if "review_button" in request.form:
            return redirect(url_for("images.image", config_id=config_id))
        if "save_button" in request.form:
            db.save_collection(
                id=config_id if isinstance(config_id, int) else None,
                name=request.form["name"],
                end_date=request.form["end_date"],
                start_date=request.form["start_date"],
                user_id=session["user_id"],
            )
            return redirect(url_for("configs.overview"))

    if config_id == "newconfig" and db.get_username(session["user_id"]) != "Admin":
        return render_template("noAdmin.html")
    if config_id == "newconfig":
        collection = {
            "name": "",
            "sum_images": 0,
            "reviewed_images": 0,
            "start_date": datetime.today().strftime("%Y-%m-%d"),
            "end_date": datetime.today().strftime("%Y-%m-%d"),
        }
        labels = ["Nicht Bewertet", "Bewertet"]
        sizes = [1, 0]
    else:
        collection = db.get_collection_info(config_id, user_id=session["user_id"])
        labels = ["Nicht Bewertet", "Positive Bewertung", "Negative Bewertung"]
        sizes = [
            collection["no_rating"],
            collection["positive_images"],
            collection["negative_images"],
        ]
        if sum(sizes) == 0:
            sizes = [1, 0, 0]

    # Create a pie chart
    plt.figure(figsize=(8, 6))
    plt.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=140)
    plt.axis("equal")  # Equal aspect ratio ensures that pie is drawn as a circle

    # Convert plot to PNG image
    img = io.BytesIO()
    plt.savefig(img, format="png")
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    return render_template("configs/configuration.html", config=collection, plot_url=plot_url)
