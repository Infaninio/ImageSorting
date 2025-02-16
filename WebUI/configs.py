import logging
import sqlite3
from datetime import datetime
from typing import Dict, Generator, Optional

from flask import Blueprint, jsonify, redirect, render_template, request, session
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
    # db = get_db()

    # if request.method == "POST":
    #     data = request.get_json()
    #     customBackend.filter_session

    return jsonify({"error": "Invalid request method"}), 405
