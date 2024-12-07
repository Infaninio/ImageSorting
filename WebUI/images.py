import io

from caching import remove_old_images
from flask import Blueprint, jsonify, redirect, render_template, request, send_file, session, url_for

from .app import executor
from .database import get_db

bp = Blueprint("images", __name__, url_prefix="/images")


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
    if "user_id" not in session:
        return redirect("/auth/login")
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
        db.add_or_update_review(user_id=user_id, image_id=image_id, review=rating)

        # Determine the next image ID based on action
        if action == "next":
            next_image_id = db.get_next_image_ids(user_id, int(session["config_id"]), image_id)
            if next_image_id:
                next_image_id = next_image_id[0]
        elif action == "previous":
            next_image_id = db.get_previous_image_id(user_id, int(session["config_id"]), image_id)
        elif action == "trash":
            db.add_or_update_review(user_id, image_id, review=0, trash=True)  # Custom function to mark image as deleted
            next_image_id = db.get_next_image_ids(user_id, int(session["config_id"]), image_id)
            if next_image_id:
                next_image_id = next_image_id[0]
        else:
            return jsonify({"success": False, "message": "Invalid action"})

        if next_image_id:
            # Fetch the star rating for the next image
            next_image_rating = db.get_review(user_id, next_image_id)
            next_image_rating = next_image_rating if next_image_rating else 0

            return jsonify(
                {"success": True, "new_image_path": f"/images/id_{next_image_id}", "rating": next_image_rating}
            )
        else:
            # If no more images, redirect back to overview
            return jsonify({"success": False, "redirect_url": url_for("configs.overview")})

    next_image_id = db.get_starting_image_id(user_id, int(session["config_id"]))
    if not next_image_id:
        return redirect(url_for("configs.overview"))
    return render_template("image_view.html", image_path=f"/images/id_{next_image_id}")


@bp.route("<image_id>")
def image(image_id: str):
    """Serve a image."""
    db = get_db()
    image_io = io.BytesIO()
    user_id = session.get("user_id", 0)
    if image_id[:3] == "pre":
        if not db.can_user_access_image(user_id=user_id, image_id=int(image_id[4:])):
            print(f"User {user_id} cant access image {int(image_id[4:])}")
            return "You are not allowed to view or review this image", 401
        image = db.get_image(image_id=int(image_id[4:]))
        image.get_preview().save(image_io, format="PNG")
        image_io.seek(0)
    else:
        if not db.can_user_access_image(user_id=user_id, image_id=int(image_id[3:])):
            return "You are not allowed to view or review this image", 401
        image = db.get_image(image_id=int(image_id[3:]))
        image.get_image(
            image_size=(session["vp_width"], session["vp_height"]) if "vp_height" in session else None
        ).save(image_io, format="PNG")
        image_io.seek(0)

    executor.submit(remove_old_images)
    return send_file(image_io, as_attachment=False, mimetype="image/png")


@bp.route("get_adjacent_images_extended/<current_image_id>", methods=("GET",))
def get_adjacent_images_extended(current_image_id):
    """Fetch multiple adjacent images for preloading (e.g., next 3, previous 3)."""
    user_id = session.get("user_id")
    db = get_db()
    config_id = int(session["config_id"])
    current_image_id = int(current_image_id[3:])

    # Fetch next and previous images
    next_image_ids = db.get_next_image_ids(user_id, config_id, current_image_id, next_images=5)
    previous_image_id = db.get_previous_image_id(user_id, config_id, current_image_id)

    # Fetch ratings for these images
    next_images = []
    for next_image_id in next_image_ids:
        next_image_rating = db.get_review(user_id, next_image_id)
        next_image_rating = next_image_rating if next_image_rating else 0
        next_images.append({"image_path": f"/images/id_{next_image_id}", "rating": next_image_rating})

    previous_images = []
    previous_image_rating = db.get_review(user_id, previous_image_id)
    previous_image_rating = previous_image_rating if previous_image_rating else 0
    previous_images.append({"image_path": f"/images/id_{previous_image_id}", "rating": previous_image_rating})

    return jsonify({"next": next_images, "previous": previous_images})


@bp.post("resize-image")
def set_image_size():
    """Set the image size for the current session."""
    if request.method == "POST":
        session["vp_width"] = request.json["width"]
        session["vp_height"] = request.json["height"]
    return jsonify({"success": True})
