import logging
import os
from io import BytesIO
from pathlib import Path
from typing import Dict, Optional

from flask import current_app
from nc_py_api import Nextcloud
from PIL import Image
from pillow_heif import register_heif_opener

register_heif_opener()
CACHE_DIR = "./Cache/"
MAX_IMAGES = 200

# Ensure your download folder exists
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

try:
    nextcloud_instance = Nextcloud(
        nextcloud_url="https://cloud.trauberg.de",
        nc_auth_user=os.environ["NEXTCLOUD_USER"],
        nc_auth_pass=os.environ["NEXTCLOUD_PASSWORD"],
    )
except KeyError:
    logging.error("Could not connect to nextcloud. Please check credentials. Switching to debug mode")
    nextcloud_instance = None


def load_image(image_path: str, image_id: Optional[int] = None) -> Image.Image:
    """Load image from the cache or from Nextcloud if not cached.

    This function checks if the image is already cached locally. If not, it fetches
    the image from Nextcloud and saves it to the cache.

    Args:
    ----
        image_path (str): The path to the image on Nextcloud.
        image_id (Optional[int], optional): An optional identifier for the image, used to cache it. Defaults to None.

    Returns:
    -------
        Image.Image: The loaded image in RGB mode.
    """
    # Check if the images is in the cache
    if image_id and os.path.exists(f"{CACHE_DIR}{image_id}.jpg"):
        image = Image.open(f"{CACHE_DIR}{image_id}.jpg")
    else:
        if current_app.debug and not nextcloud_instance:
            image = Image.open(image_path)
        else:
            rgb_image = nextcloud_instance.files.download(image_path)
            image = Image.open(BytesIO(rgb_image))
        if image_id:
            image.save(f"{CACHE_DIR}{image_id}.jpg", exif=image.getexif())
    return image


def cache_images(image_ids: Dict[int, str]):
    """Cache multiple images by their IDs and paths.

    This function iterates through the provided dictionary of image IDs and their
    corresponding Nextcloud paths, loading each image and caching it locally.

    Args:
    ----
        image_ids (Dict[int, str]): A dictionary mapping image IDs to their Nextcloud paths.
    """
    for image_id, image_path in image_ids.items():
        load_image(image_id=image_id, image_path=image_path)


def static_cache(image_ids: Dict[int, str]):
    """Cache the provided images and writes a cache tracking file.

    This function caches the images and then creates or updates a file called "_ignore_.txt"
    in the cache directory, which tracks the images that are cached and should not be deleted.

    Args:
    ----
        image_ids (Dict[int, str]): A dictionary mapping image IDs to their Nextcloud paths.
    """
    cache_images(image_ids=image_ids)
    with open(Path(CACHE_DIR, "_ignore_.txt"), "w+") as file:
        file.writelines([f"{key}.jpg\n" for key in image_ids.keys()])


def remove_old_images():
    """Remove the oldest cached images to keep the cache size within the limit.

    This function checks the number of files in the cache directory and deletes
    the oldest files if the total number exceeds the `MAX_IMAGES` limit. The files to
    exclude from deletion are tracked in the "_ignore_.txt" file.

    This function ensures that only the most recent images are kept in the cache
    and older, unused images are removed automatically.
    """
    try:
        with open(Path(CACHE_DIR, "_ignore_.txt"), "r") as file:
            exception_list = file.readlines()
    except FileNotFoundError:
        exception_list = []

    files = [
        (f, os.path.getmtime(os.path.join(CACHE_DIR, f)))
        for f in os.listdir(CACHE_DIR)
        if os.path.isfile(os.path.join(CACHE_DIR, f)) and f not in exception_list
    ]
    num_to_remove = max(0, len(files) - MAX_IMAGES)
    files.sort(key=lambda x: x[1])  # Sort by the second element, which is the modification time

    for i in range(num_to_remove):
        file_to_remove = files[i][0]
        file_path = os.path.join(CACHE_DIR, file_to_remove)
        print(f"Removing oldest image: {file_to_remove}")
        os.remove(file_path)
