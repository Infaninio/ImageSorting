import io

from flask import Blueprint, redirect, render_template, request, send_file, url_for

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


@bp.route("<config_id>/next", methods=("GET", "POST"))
def next_image(config_id: int):
    """Display image deciding site.

    Parameters
    ----------
    config_id : str
        Name of the image.

    """
    if request.method == "POST":
        print(request.form["page"])
        if "decline" == request.form["page"]:
            return redirect(url_for("images.image", config_id=config_id))
        if "accept" == request.form["page"]:
            return redirect(url_for("images.image", config_id=config_id))

    return render_template("image_view.html", image_path="/static/images/default.jpg")


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
