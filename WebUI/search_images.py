import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import List

from nc_py_api import Nextcloud

from .database import ImageTinderDatabase
from .Image import Custom_Image


def get_image_files(dir: str, nextcloud_instance: Nextcloud) -> List[str]:
    """Find all (recursive) image files in a nextcloud folder.

    Allowed formates are [png, jpg, jpeg, png, heic]

    Args:
    ----
        dir (str): Parent directory where to start the search.
        nextcloud_instance (Nextcloud): A nextcloud instance to connect to.

    Returns:
    -------
        List[str]: A list of all found image files
    """
    image_files = []
    for node in nextcloud_instance.files.listdir(dir):
        if node.is_dir:
            image_files.extend(get_image_files(node.user_path, nextcloud_instance))
        elif Path(node.user_path).suffix.lower() in [".png", ".jpg", ".jpeg", ".png", ".heic"]:
            image_files.append(node.user_path)

    return image_files


def process_image(image):
    """Process a single image by adding or updating it in the database."""
    database = ImageTinderDatabase(database_name="./ImageSorting.sqlite")
    database.add_or_update_image(Custom_Image(image_id=0, path=image))


def main():
    """Search for images in the nextcloud and add to database."""
    nc = Nextcloud(
        nextcloud_url=os.environ["NEXTCLOUD_URL"],
        nc_auth_user=os.environ["NEXTCLOUD_USER"],
        nc_auth_pass=os.environ["NEXTCLOUD_PASSWORD"],
    )

    images = get_image_files("/Photos/", nc)
    # Parallelize the add_or_update_image calls
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_image, image) for image in images]

        # Optionally wait for all tasks to complete (if needed)
        for future in futures:
            future.result()


if __name__ == "__main__":
    main()
