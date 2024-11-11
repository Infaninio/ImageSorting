import os
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


if __name__ == "__main__":
    nc = Nextcloud(
        nextcloud_url="https://cloud.trauberg.de",
        nc_auth_user=os.environ["NEXTCLOUD_USER"],
        nc_auth_pass=os.environ["NEXTCLOUD_PASSWORD"],
    )
    database = ImageTinderDatabase(database_name="./ImageSorting.sqlite")

    images = get_image_files("/Photos/", nc)
    for image in images:
        database.add_or_update_image(Custom_Image(image))
