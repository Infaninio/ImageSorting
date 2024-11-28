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
    return redirect(url_for("images.review"))


@bp.route("review", methods=("GET", "POST"))
def review():
    """Load first review page, or get next review image."""
    user_id = session.get("user_id")
    db = get_db()
    if request.method == "POST":
        # Extract form data
        action = request.form["page"]  # 'next', 'previous', or 'trash'
        image_id = request.form["image_id"]
        image_id = int(image_id[3:])
        rating = int(request.form.get("rating", 0))  # Default to 0 if no rating
        print(f"Image: {image_id} with rating {rating}")
        # Save the review in the database
        db.add_or_update_review(user_id=user_id, image_id=image_id, review={"star": rating})

        # Determine the next image ID based on action
        if action == "next":
            next_image_id = db.get_next_image_ids(user_id, int(session["config_id"]), image_id)[0]
        elif action == "previous":
            next_image_id = db.get_previous_image_id(user_id, int(session["config_id"]), image_id)
        elif action == "trash":
            db.add_or_update_review(
                user_id, image_id, review={"trash": True}
            )  # Custom function to mark image as deleted
            next_image_id = db.get_next_image_ids(user_id, int(session["config_id"]), image_id)[0]
        else:
            return jsonify({"success": False, "message": "Invalid action"})

        if next_image_id:
            # Fetch the star rating for the next image
            next_image_rating = db.get_review(user_id, next_image_id)
            next_image_rating = next_image_rating.get("star", 0) if next_image_rating else 0

            return jsonify(
                {"success": True, "new_image_path": f"/images/id_{next_image_id}", "rating": next_image_rating}
            )
        else:
            # If no more images, redirect back to overview
            return jsonify({"success": False, "redirect_url": url_for("configs.overview")})

    next_image_id = db.get_starting_image_id(user_id, int(session["config_id"]))
    return render_template("image_view.html", image_path=f"/images/id_{next_image_id}")


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
