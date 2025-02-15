import argparse
import datetime
from pathlib import Path
from typing import List

from .database import ImageTinderDatabase
from .Image import Custom_Image


def get_image_files(image_dir: Path) -> List[Path]:
    """Return a list of all jpg files in the image_dir."""
    return [f for f in image_dir.rglob("*.jpg")]


def add_images_to_database(image_dir: Path, nr_images: int):
    """Add images to the database.

    Args:
    ----
        image_dir (Path): The directory where the images are stored.
        nr_images (int): The number of images to add to the database.
        If there are less images in the directory than nr_images, the images will be added in a loop
    """
    image_files = get_image_files(image_dir)
    database = ImageTinderDatabase(database_name="./ImageSorting.sqlite")
    today = datetime.datetime.now()
    for i_id in range(nr_images):
        image_date = today - datetime.timedelta(days=i_id)
        database.add_image_to_database(
            Custom_Image(image_id=i_id, path=image_files[i_id % len(image_files)], date=image_date)
        )


def add_collections_to_database(nr_images):
    """Create 5 collections.

    The first one with all images, second with the first 20%, third with 15%-50%,
    fourth with 45%-80% and fifth with the last 50%.
    """
    database = ImageTinderDatabase(database_name="./ImageSorting.sqlite")
    start_day = datetime.datetime.now() - datetime.timedelta(days=nr_images + 1)
    database.save_collection("All images", start_date=start_day, end_date=datetime.datetime.now())
    database.save_collection(
        "First 20%", start_date=start_day, end_date=start_day + datetime.timedelta(days=nr_images * 0.2)
    )
    database.save_collection(
        "15%-50%",
        start_date=start_day + datetime.timedelta(days=nr_images * 0.15),
        end_date=start_day + datetime.timedelta(days=nr_images * 0.5),
    )
    database.save_collection(
        "45%-80%",
        start_date=start_day + datetime.timedelta(days=nr_images * 0.45),
        end_date=start_day + datetime.timedelta(days=nr_images * 0.8),
    )
    database.save_collection(
        "Last 50%", start_date=start_day + datetime.timedelta(days=nr_images * 0.5), end_date=datetime.datetime.now()
    )


def add_users_to_database():
    """Add 3 users to the database."""
    database = ImageTinderDatabase(database_name="./ImageSorting.sqlite")
    database.create_user("User1", "password")
    database.create_user("User2", "password")
    database.create_user("User3", "password")


def add_users_to_collections():
    """Add users to collections."""
    database = ImageTinderDatabase(database_name="./ImageSorting.sqlite")
    user_1 = database.get_user_id_from_table("User1", "password")
    user_2 = database.get_user_id_from_table("User2", "password")
    user_3 = database.get_user_id_from_table("User3", "password")
    database.add_user_to_collection(user_1, 1)
    database.add_user_to_collection(user_1, 2)
    database.add_user_to_collection(user_1, 3)
    database.add_user_to_collection(user_1, 4)
    database.add_user_to_collection(user_1, 5)

    database.add_user_to_collection(user_2, 1)
    database.add_user_to_collection(user_2, 2)
    database.add_user_to_collection(user_3, 3)
    database.add_user_to_collection(user_3, 4)
    database.add_user_to_collection(user_2, 5)


def main():
    """Run the script to setup the development environment."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--image-dir", "-i", type=Path, required=True)
    parser.add_argument("--nr-images", "-n", type=int, default=2000)
    args = parser.parse_args()

    add_images_to_database(args.image_dir, args.nr_images)
    add_collections_to_database(args.nr_images)
    add_users_to_database()
    add_users_to_collections()


main()
