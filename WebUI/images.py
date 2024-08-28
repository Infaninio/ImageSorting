from flask import Blueprint, redirect, render_template, request, url_for

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
def image(config_id: int):
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
