import sqlite3
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

from WebUI.database import ImageTinderDatabase as DB
from WebUI.database import UserAlreadyExists, UserNotExisting, WrongPassword


class TestImageSelector(unittest.TestCase):
    """Test ImageSelector class."""

    def __init__(self, methodName: str = "Test SelectorImage class") -> None:
        """Set up Testclass."""
        super().__init__(methodName)
        connection = sqlite3.connect("test.sqlite")
        self.cursor = connection.cursor()
        self.set_up_database()

        self.db = DB(database_name="test.sqlite")

    def set_up_database(self):
        with open(Path(Path(__file__).parent.parent.parent, "ImageSorting/Database/schema.sql")) as sql_file:
            data = sql_file.read().replace("\n", "").split(";")
            for query in data:
                if query:
                    self.cursor.execute(query)

        with open(Path(Path(__file__).parent.parent.parent, "ImageSorting/Database/fill_table.sql")) as sql_file:
            data = sql_file.read().replace("\n", "").split(";")
            for query in data:
                if query:
                    self.cursor.execute(query + ";")
        self.cursor.connection.commit()

    def test_create_user(self):
        self.db.create_user("user11@example.com", "asdf1234")
        self.cursor.execute("SELECT email FROM user WHERE user.email = 'user11@example.com'")
        self.assertListEqual(list(self.cursor), [("user11@example.com",)])

        with self.assertRaises(UserAlreadyExists):
            self.db.create_user("user11@example.com", "asdf1235")

    def mock_check_password(self, password, password_hash):
        return password == password_hash

    @patch("WebUI.database.db_wrapper.check_password_hash")
    def test_user_authentication(self, check_password: MagicMock):
        check_password.side_effect = self.mock_check_password
        user_id = self.db.get_user_id_from_table("user10@example.com", "securepasswordxyz")
        self.assertLess(user_id, 11)

        with self.assertRaises(WrongPassword):
            user_id = self.db.get_user_id_from_table("user10@example.com", "wrongPassword")

        with self.assertRaises(UserNotExisting):
            user_id = self.db.get_user_id_from_table("unknow@user.com", "apassword")

    @patch("WebUI.database.db_wrapper.check_password_hash")
    def test_get_username(self, check_password: MagicMock):
        check_password.side_effect = self.mock_check_password
        user_id = self.db.get_user_id_from_table("user10@example.com", "securepasswordxyz")
        self.assertEqual(self.db.get_username(user_id), "user10@example.com")

    def test_get_user_collections(self):
        result = self.db.get_user_collections(1)
        expected_result = [
            {
                "name": "collection1",
                "start_date": datetime(2023, 6, 1),
                "end_date": datetime(2023, 9, 1),
                "id": 1,
            },
            {
                "name": "collection2",
                "start_date": datetime(2024, 7, 15),
                "end_date": datetime(2024, 7, 20),
                "id": 2,
            },
            {
                "name": "collection3",
                "start_date": datetime(2024, 3, 1),
                "end_date": datetime(2024, 3, 31),
                "id": 3,
            },
        ]
        self.assertListEqual(result, expected_result)

        result = self.db.get_user_collections(5)
        expected_result = [
            {
                "name": "collection2",
                "start_date": datetime(2024, 7, 15),
                "end_date": datetime(2024, 7, 20),
                "id": 2,
            },
            {
                "name": "collection3",
                "start_date": datetime(2024, 3, 1),
                "end_date": datetime(2024, 3, 31),
                "id": 3,
            },
        ]
        self.assertListEqual(result, expected_result)

        result = self.db.get_user_collections(22)
        expected_result = []
        self.assertListEqual(result, expected_result)

    def test_new_collection(self):
        self.db.save_collection(
            name="collection4",
            start_date=datetime(2023, 2, 3),
            end_date=datetime(2024, 3, 4),
            user_id=1,
        )
        collections = self.db.get_user_collections(1)
        self.assertIn(
            {
                "name": "collection4",
                "start_date": datetime(2023, 2, 3),
                "end_date": datetime(2024, 3, 4),
                "id": 4,
            },
            collections,
        )

    def test_update_collection(self):
        self.db.save_collection(
            name="updated_collection",
            start_date=datetime(2023, 2, 3),
            end_date=datetime(2024, 3, 4),
            user_id=1,
            id=1,
        )
        collections = self.db.get_user_collections(1)
        self.assertIn(
            {
                "name": "updated_collection",
                "start_date": datetime(2023, 2, 3),
                "end_date": datetime(2024, 3, 4),
                "id": 1,
            },
            collections,
        )

    def test_get_collections(self):
        result = self.db.get_user_collections(5)
        expected_result = [
            {
                "name": "collection2",
                "start_date": datetime(2024, 7, 15),
                "end_date": datetime(2024, 7, 20),
                "id": 2,
            },
            {
                "name": "collection3",
                "start_date": datetime(2024, 3, 1),
                "end_date": datetime(2024, 3, 31),
                "id": 3,
            },
        ]
        self.assertListEqual(result, expected_result)

        result = self.db.get_user_collections(9)
        expected_result = [
            {
                "name": "collection3",
                "start_date": datetime(2024, 3, 1),
                "end_date": datetime(2024, 3, 31),
                "id": 3,
            }
        ]
        self.assertListEqual(result, expected_result)

        result = self.db.get_user_collections(10)
        expected_result = []
        self.assertListEqual(result, expected_result)

    def test_get_collection_info(self):
        result = self.db.get_collection_info(1, 1)
        expectation = {
            "name": "collection1",
            "images": 8,
            "positive_images": 1,
            "negative_images": 2,
            "no_rating": 5,
            "start_date": datetime(2023, 6, 1),
            "end_date": datetime(2023, 9, 1),
        }
        self.assertDictEqual(result, expectation)

        result = self.db.get_collection_info(1, 2)
        expectation = {
            "name": "collection1",
            "images": 8,
            "positive_images": 3,
            "negative_images": 0,
            "no_rating": 5,
            "start_date": datetime(2023, 6, 1),
            "end_date": datetime(2023, 9, 1),
        }

        self.assertDictEqual(result, expectation)

    def test_get_image_id(self):
        result_id = self.db.get_image_id_by_path("/path/to/image1.jpg")
        self.assertIsNotNone(result_id)

        result_id = self.db.get_image_id_by_path("/path/to/notExisting.jpg")
        self.assertIsNone(result_id)

        result_id = self.db.get_image_id_by_path("/path/to/image01.jpg")
        self.assertIsNone(result_id)


if __name__ == "__main__":
    unittest.main()
