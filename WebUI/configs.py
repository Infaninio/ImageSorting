import io
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from tempfile import gettempdir
from typing import Dict, Generator, Optional
from zipfile import ZipFile

from flask import Blueprint, jsonify, redirect, render_template, request, send_file, session
from typeguard import typechecked

from .database import get_db


class Backend:
    """Backend class to manage sessions and generators."""

    def __init__(self):
        """Backend class to manage sessions and generators."""
        self.generators: Dict[int, Generator[None, None, int]] = {}

    @typechecked
    def add_session(self, session_id: str, config_id: int):
        print(f"-----------\n Adding Session with ID {session_id}")
        self.generators[session_id] = self.image_gallery_generator(config_id=config_id)

    @typechecked
    @staticmethod
    def image_gallery_generator(config_id: int) -> Generator[int, None, None]:
        db = get_db()
        ids = db.get_all_image_ids(config_id=config_id)

        for image_id in ids:
            yield image_id

    @typechecked
    @staticmethod
    def filter_image_generator(
        config_id: int, user_id: int, min_rating: int, max_results_per_day: int
    ) -> Generator[int, None, None]:
        db = get_db()
        ids = db.get_images_ids_filtered(
            config_id=config_id, user_id=user_id, min_rating=min_rating, max_results_per_day=max_results_per_day
        )
        print(f"Filtered ids: {ids}")
        for image_id in ids:
            yield image_id

    @typechecked
    def add_filtered_image_generator(
        self, session_id: str, config_id: int, user_id: int, min_rating: int = 0, max_results_per_day: int = 0
    ):
        self.generators[session_id] = self.filter_image_generator(
            config_id=config_id,
            user_id=user_id,
            min_rating=min_rating,
            max_results_per_day=max_results_per_day,
        )

    @typechecked
    def get_next_image(self, session_id: str) -> Optional[int]:
        try:
            return next(self.generators[session_id])
        except StopIteration:
            return None


customBackend = Backend()

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
        can_user_add_user_to_collection=db.can_user_create_collection(session["user_id"]),
    )


@bp.route("/gallery/<collection_id>", methods=("GET", "POST"))
def gallery(collection_id):
    """Show all images of the collection in a gallery."""
    customBackend.add_session(session["uuid"], int(collection_id))
    return render_template(
        "configs/gallery.html",
    )


@bp.route("/new_config", methods=("GET", "POST"))
def new_config():
    """Create a new configuration."""
    db = get_db()
    if not db.can_user_create_collection(session["user_id"]):
        return jsonify({"error": "You are not allowed to create a new collection."}), 403

    if request.method == "POST":
        data = request.get_json()
        name = data.get("title")
        startDate = datetime.strptime(data.get("startDate"), "%Y-%m-%d")
        endDate = datetime.strptime(data.get("endDate"), "%Y-%m-%d")

        logging.debug(f"new_config: {request.get_json()}")
        collection_id = db.add_collection(name, startDate, endDate, user_id=session["user_id"])
        collection = db.get_collection_info(collection_id, user_id=session["user_id"])
        result = collection.dict
        result["success"] = True
        return jsonify(result)
    else:
        return jsonify({"success": False})


@bp.route("/get_users", methods=("GET", "POST"))
def get_users():
    """Get all users of a collection."""
    if request.method == "POST":
        collection_id = request.get_json().get("collectionId")
        db = get_db()
        if not db.can_user_create_collection(session["user_id"]):
            return jsonify({"error": "You are not allowed to add users to collections."}), 403

        users = db.get_all_users(collection_id)
        return jsonify(users)

    return jsonify({"error": "Invalid request method"}), 405


@bp.route("/add_user_to_collection", methods=("GET", "POST"))
def add_user_to_collection():
    """Add a user to a collection."""
    db = get_db()
    if not db.can_user_create_collection(session["user_id"]):
        return jsonify({"error": "You are not allowed to add users to collections."}), 403

    if request.method == "POST":
        data = request.get_json()
        collection_id = data.get("collectionId")
        users = data.get("users")
        for user_id in users:
            try:
                db.add_user_to_collection(user_id=user_id, collection_id=collection_id)
            except sqlite3.IntegrityError:
                # Thats ok user already part of the collection
                pass

        return jsonify({"success": True})
    else:
        return jsonify({"error": "Invalid request method"}), 405


@bp.route("/filter", methods=("GET", "POST"))
def filter():
    """Set a filter generator for the image gallery."""
    if request.method == "POST":
        data = request.get_json()
        config_id = int(request.referrer.split("/")[-1])
        if (data.get("minRating", 0) == 0) and (int(data.get("bestOfDay", 0)) == 0):
            customBackend.add_session(session_id=session["uuid"], config_id=config_id)
        else:
            customBackend.add_filtered_image_generator(
                session_id=session["uuid"],
                config_id=config_id,
                user_id=session["user_id"],
                min_rating=data.get("minRating", 0),
                max_results_per_day=int(data.get("bestOfDay", 0)),
            )
        return jsonify({"success": True})

    return jsonify({"error": "Invalid request method"}), 405


@bp.route("/download_gallery", methods=("GET", "POST"))
def download_gallery():
    """Create a zip file of all selected images and download it."""
    if not request.method == "POST":
        return jsonify({"error": "Invalid request method"}), 405

    temp_dir = gettempdir()
    db = get_db()
    # Create a new ZIP file and add the images to it
    zip_filename = "images.zip"
    data = request.get_json()
    config_id = int(request.referrer.split("/")[-1])
    if (data.get("minRating", 0) == 0) and (int(data.get("bestOfDay", 0)) == 0):
        images = Backend.image_gallery_generator(config_id=config_id)
    else:
        images = Backend.filter_image_generator(
            user_id=session["user_id"],
            config_id=config_id,
            min_rating=data.get("minRating", 0),
            max_results_per_day=int(data.get("bestOfDay", 0)),
        )
    try:
        with ZipFile(Path(temp_dir, zip_filename), "w") as zip_file:
            print(temp_dir)
            for file_id in images:
                img = db.get_image(file_id)
                img_buffer = io.BytesIO()
                img.get_image().save(img_buffer, format="JPEG" if img.name.endswith(".jpg") else "PNG")
                img_buffer.seek(0)

                zip_file.writestr(img.name, img_buffer.read())

        # Return the ZIP file to the client
        return send_file(Path(temp_dir, zip_filename), as_attachment=True)

    finally:
        # shutil.rmtree(temp_dir)
        pass
