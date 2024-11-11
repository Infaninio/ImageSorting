import os
import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional

from flask import g
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

    def get_user_collections(self, user_id: int) -> List[Dict[str, Any]]:
        query = f"""SELECT collection.name, collection.start_date, collection.end_date, collection.id
                    FROM collection INNER JOIN user_collection ON user_collection.collection_id=collection.id
                    WHERE user_collection.user_id={user_id};"""
        data = self._execute_sql(query, get_result=True)
        return [
            {
                "name": res[0],
                "start_date": datetime.fromisoformat(res[1]),
                "end_date": datetime.fromisoformat(res[2]),
                "id": res[3],
            }
            for res in data
        ]

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

    def get_collection_info(self, collection_id: int, user_id: int) -> Dict[str, Any]:
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

        no_rating, positiv_rating, negativ_rating = 0, 0, 0

        for image in images:
            if image[4] == "like":
                positiv_rating += 1
            elif image[4] == "dislike":
                negativ_rating += 1
            elif image[4] == "no_rating":
                no_rating += 1
            else:
                print(f"Unknown rating: {image[4]}")
        configuration = {
            "name": collection[0][0],
            "images": len(images),
            "positive_images": positiv_rating,
            "negative_images": negativ_rating,
            "no_rating": no_rating,
            "start_date": datetime.fromisoformat(start_date),
            "end_date": datetime.fromisoformat(end_date),
        }
        return configuration

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


def get_db() -> ImageTinderDatabase:
    """Get the database handler."""
    if "db" not in g:
        g.db = ImageTinderDatabase()

    return g.db
