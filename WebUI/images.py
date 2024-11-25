import io

from flask import Blueprint, jsonify, redirect, render_template, request, send_file, session, url_for

from .database import get_db

bp = Blueprint("images", __name__, url_prefix="/images")


class Image:
    """Simple class for handling images."""

    def __hash__(self) -> int:
        """Build hash of image."""
        raise NotImplementedError

    def get_image(self) -> str:
        raise NotImplementedError

    def get_preview(self) -> str:
        raise NotImplementedError


@bp.route("/", methods=("GET", "POST"))
def overview():
    """Overviewpage of the configurations."""
    return redirect(url_for("configs.overview"))


@bp.route("review/<config_id>", methods=("GET", "POST"))
def init_review(config_id: str):
    """Display image deciding site.

    Parameters
    ----------
    config_id : str
        Name of the image.

    """
    session["config_id"] = config_id
    session["current_image"] = 1
    return redirect(url_for("images.review"))


@bp.route("review", methods=("GET", "POST"))
def review():
    """Load first review page, or get next review image."""
    user_id = session.get("user_id")
    if request.method == "POST":
        print(request.form["page"])
        db = get_db()
        image_id = request.form["image_id"]
        image_id = int(image_id[image_id.rfind("id_") + 3 :])
        print(image_id)
        # old_review = db.get_review(user_id=user_id, image_id=image_id)
        print(request.form)
        new_rating = int(request.form["rating"])
        db.add_or_update_review(user_id=user_id, image_id=image_id, review={"star": new_rating})

        if "next" == request.form["page"]:
            return jsonify({"success": True, "new_image_path": f"/images/id_{2}"})
        if "previous" == request.form["page"]:
            return jsonify({"success": True, "new_image_path": f"/images/id_{1}"})
        if "trash" == request.form["page"]:
            return jsonify({"success": True, "new_image_path": f"/images/id_{3}"})

    return render_template("image_view.html", image_path=f"/images/id_{1}")


@bp.route("<image_id>")
def image(image_id: str):
    """Serve a image."""
    db = get_db()
    image_io = io.BytesIO()
    if image_id[:3] == "pre":
        image = db.get_image(image_id=int(image_id[4:]))
        image.get_preview().save(image_io, format="PNG")
        image_io.seek(0)
    else:
        image = db.get_image(image_id=int(image_id[3:]))
        image.get_image().save(image_io, format="PNG")
        image_io.seek(0)
    return send_file(image_io, as_attachment=False, mimetype="image/png")
