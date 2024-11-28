import json
import os
import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional

from flask import g
from typeguard import typechecked
from werkzeug.security import check_password_hash, generate_password_hash

from WebUI.Image import Custom_Image


class UserNotExisting(Exception):
    """Exception for non existing user."""

    pass


class UserAlreadyExists(Exception):
    """Exception for already existing user."""

    pass


class WrongPassword(Exception):
    """Exception for wrong password."""

    pass


class Collection:
    """A class representing a collection of images.

    Attributes
    ----------
        name (str): The name of the collection.
        images (int): The number of images in the collection.
        start_date (datetime): The start date of the collection, as an ISO-formatted datetime object.
        end_date (datetime): The end date of the collection, as an ISO-formatted datetime object.
        preview_image (Optional[int]): The index of the preview image in the collection. Defaults to None.

    Methods
    -------
        start_date_str: A property returning the start date as a string in the format "DD MMM YYYY".
        end_date_str: A property returning the end date as a string in the format "DD MMM YYYY".
        dict: A property returning a dictionary representation of the collection.
    """

    def __init__(
        self, id: int, name: str, images: int, start_date: str, end_date: str, preview_image: Optional[int] = None
    ):
        """Initialize a new instance of the Collection class.

        Args:
        ----
            id (int): Unique id of the collection.
            name (str): The name of the collection.
            images (int): The number of images in the collection.
            start_date (str): The start date of the collection as an ISO-formatted string.
            end_date (str): The end date of the collection as an ISO-formatted string.
            preview_image (Optional[int]): The index of the preview image in the collection. Defaults to None.
        """
        self.id = id
        self.name = name
        self.images = images
        self.start_date = datetime.fromisoformat(start_date)
        self.end_date = datetime.fromisoformat(end_date)
        self.preview_image = preview_image

    @property
    def start_date_str(self) -> str:
        """Returns the start date as a string in the format "DD MMM YYYY"."""
        return self.start_date.strftime("%d %B %Y")

    @property
    def end_date_str(self) -> str:
        """Returns the end date as a string in the format "DD MMM YYYY"."""
        return self.end_date.strftime("%d %B %Y")

    @property
    def dict(self) -> Dict[str, Any]:
        """Get a dictionary representation of the collection."""
        return {
            "url": f"/images/review/{self.id}",
            "image_uri": f"/images/pre_{self.preview_image}" if self.preview_image else "/static/images/default.jpg",
            "name": self.name,
            "start_date": self.start_date_str,
            "end_date": self.end_date_str,
        }


class ImageTinderDatabase:
    """Wrapper for the ImageTinder Database to be easy usable from outside."""

    def __init__(self, database_name: str = "../ImageSorting.sqlite") -> None:
        """Create the database wrapper.

        Parameters
        ----------
        database_name : str, optional
            Name of the sqlite file, by default "ImageSorting.sqlite"
        """
        self.connection = sqlite3.connect(database_name)
        try:
            self.get_user_id_from_table("Admin", "test123")
        except UserNotExisting:
            admin_pass = os.environ.get("IMAGE_SORTING_ADMIN_PASS")
            self.create_user("Admin", admin_pass)
        except WrongPassword:
            pass

    def _execute_sql(self, statement: str, get_result: bool = False) -> Optional[List[Any]]:
        with self.connection:
            cur = self.connection.execute(statement)
            if get_result:
                return list(cur)
            else:
                return None

    def get_user_id_from_table(self, username: str, password: str) -> int:
        query = f"SELECT * FROM user WHERE user.email = '{username}';"
        result = self._execute_sql(query, get_result=True)
        if not result:
            raise UserNotExisting
        if not check_password_hash(result[0][2], password):
            raise WrongPassword

        return result[0][0]

    def get_username(self, user_id: int) -> str:
        query = f"SELECT email FROM user WHERE user.id = '{user_id}';"
        return self._execute_sql(query, get_result=True)[0][0]

    def create_user(self, username: str, password: str):
        query = f"SELECT * FROM user WHERE user.email = '{username}';"
        password_hash = generate_password_hash(password=password)
        result = self._execute_sql(query, get_result=True)
        if result:
            raise UserAlreadyExists

        query = f"INSERT INTO user (email, password) VALUES ('{username}', '{password_hash}');"
        self._execute_sql(query)
        self.connection.commit()

    def get_user_collections(self, user_id: int) -> List[Collection]:
        query = f"""SELECT collection.id
                    FROM collection INNER JOIN user_collection ON user_collection.collection_id=collection.id
                    WHERE user_collection.user_id={user_id};"""
        data = self._execute_sql(query, get_result=True)
        return [self.get_collection_info(result[0], 0) for result in data]

    def save_collection(
        self,
        name: str,
        start_date: datetime,
        end_date: datetime,
        user_id: int,
        id: Optional[int] = None,
    ):
        if id:
            query = f"""UPDATE collection SET name='{name}', start_date='{start_date}', end_date='{end_date}'
                        WHERE id={id};"""
            self._execute_sql(query)
        else:
            query = f"""INSERT INTO collection (name, start_date, end_date)
                        VALUES ('{name}', '{start_date}', '{end_date}')
                        RETURNING id;"""
            new_id = self._execute_sql(query, get_result=True)
            self.add_user_to_collection(user_id, new_id[0][0])

        self.connection.commit()

    def add_user_to_collection(self, user_id: int, collection_id: int):
        query = f"INSERT INTO user_collection (user_id, collection_id) VALUES ({user_id}, {collection_id})"
        self._execute_sql(query)

    @typechecked
    def get_collection_info(self, collection_id: int, user_id: int) -> Collection:
        query = f"""SELECT collection.name, collection.start_date, collection.end_date
                    FROM collection
                    WHERE collection.id={collection_id};"""
        collection = self._execute_sql(query, get_result=True)
        start_date = collection[0][1]
        end_date = collection[0][2]
        query = f"""SELECT i.id AS image_id, i.file_path, i.creation_date, i.image_location,
                    COALESCE(ui.rating, 'no_rating') AS user_rating
                    FROM image i LEFT JOIN user_image ui ON i.id = ui.image_id AND ui.user_id = {user_id}
                    WHERE i.creation_date BETWEEN '{start_date}' AND '{end_date}';"""
        images = self._execute_sql(query, get_result=True)

        collection = Collection(
            id=collection_id,
            name=collection[0][0],
            images=len(images),
            start_date=start_date,
            end_date=end_date,
            preview_image=images[0][0],
        )

        return collection

    def get_image_id(self, img_path: str) -> Optional[int]:
        query = f"SELECT id FROM image WHERE image.file_path = '{img_path}';"

        result = self._execute_sql(query, get_result=True)
        if not result:
            return None
        return result[0][0]

    def add_or_update_image(self, image: Custom_Image, update: bool = False):
        img_id = self.get_image_id(image.path)
        if img_id and not update:
            return

        date = image.get_date()
        location = image.get_location()

        if img_id:
            query = f"""UPDATE image SET creation_date='{date}', image_location='{location}' WHERE id={img_id};"""
            self._execute_sql(query)
        else:
            query = f"""INSERT INTO image (file_path, creation_date, image_location)
                        VALUES ('{image.path}', '{date}', '{location}')"""
            self._execute_sql(query)

    def get_image(self, image_id: int) -> Custom_Image:
        query = f"""SELECT * FROM image WHERE image.id={image_id}"""
        result = self._execute_sql(query, True)[0]

        return Custom_Image(path=result[1], location=result[3], date=result[2])

    @typechecked
    def get_review(self, user_id: int, image_id: int) -> Optional[Dict[str, Any]]:
        query = f"""SELECT rating
                   FROM user_image
                   WHERE user_id = {user_id} AND image_id = {image_id};"""
        return_value = self._execute_sql(query, True)
        if return_value:
            return json.loads(return_value[0][0])
        else:
            return None

    @typechecked
    def add_or_update_review(self, user_id: int, image_id: int, review: Dict[str, Any]):
        old_review = self.get_review(user_id=user_id, image_id=image_id)

        if old_review:
            old_review.update(review)
            query = f"""UPDATE user_image SET rating='{json.dumps(old_review)}'
                        WHERE user_id={user_id} AND image_ID={image_id};"""
        else:
            query = f"""INSERT INTO user_image (user_id, image_id, rating)
                        VALUES ({user_id}, {image_id}, '{json.dumps(review)}');"""

        self._execute_sql(query)

    @typechecked
    def get_starting_image_id(
        self,
        user_id: int,
        config_id: int,
    ) -> int:
        query = f"""WITH images_in_collection AS (
                SELECT i.id, i.file_path, i.creation_date, i.image_location
                FROM image i
                INNER JOIN collection c
                    ON i.creation_date BETWEEN c.start_date AND c.end_date
                WHERE c.id = {config_id}
            ),
            unreviewed_images AS (
                SELECT i.id, i.file_path, i.creation_date, i.image_location
                FROM images_in_collection i
                LEFT JOIN user_image ui
                    ON i.id = ui.image_id AND ui.user_id = {user_id}
                WHERE ui.image_id IS NULL -- Exclude images already reviewed by the user
            )
            SELECT *
            FROM unreviewed_images
            ORDER BY creation_date ASC
            LIMIT 1;

            """

        results = self._execute_sql(query, True)
        return results[0][0]

    @typechecked
    def get_next_image_ids(self, user_id: int, config_id: int, current_id: int, next_images: int = 1) -> List[int]:
        next_images = max(1, next_images)
        query = f"""WITH user_images_in_config AS (
                    SELECT i.id AS image_id, i.creation_date
                    FROM image i
                    INNER JOIN collection c
                        ON i.creation_date BETWEEN c.start_date AND c.end_date
                    INNER JOIN user_collection uc
                        ON uc.collection_id = c.id
                    WHERE uc.user_id = {user_id}
                    AND c.id = {config_id}
                )
                SELECT image_id
                FROM user_images_in_config
                WHERE creation_date > (
                    SELECT creation_date
                    FROM image
                    WHERE id = {current_id}
                )
                ORDER BY creation_date ASC
                LIMIT {next_images}

            """

        results = self._execute_sql(query, True)
        return [result[0] for result in results]

    @typechecked
    def get_previous_image_id(self, user_id: int, config_id: int, current_id: int):
        query = f"""WITH user_images_in_config AS (
                    SELECT i.id AS image_id, i.creation_date
                    FROM image i
                    INNER JOIN collection c
                        ON i.creation_date BETWEEN c.start_date AND c.end_date
                    INNER JOIN user_collection uc
                        ON uc.collection_id = c.id
                    WHERE uc.user_id = {user_id}
                    AND c.id = {config_id}
                )
                SELECT image_id
                FROM user_images_in_config
                WHERE creation_date < (
                    SELECT creation_date
                    FROM image
                    WHERE id = {current_id}
                )
                ORDER BY creation_date DESC
                LIMIT 1;
                """
        results = self._execute_sql(query, True)
        return results[0][0]


def get_db() -> ImageTinderDatabase:
    """Get the database handler."""
    if "db" not in g:
        g.db = ImageTinderDatabase()

    return g.db
