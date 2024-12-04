import os
from io import BytesIO

from nc_py_api import Nextcloud
from PIL import Image
from pillow_heif import register_heif_opener

register_heif_opener()
CACHE_DIR = "./Cache/"
MAX_IMAGES = 200

if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)


nextcloud_instance = Nextcloud(
    nextcloud_url="https://cloud.trauberg.de",
    nc_auth_user=os.environ["NEXTCLOUD_USER"],
    nc_auth_pass=os.environ["NEXTCLOUD_PASSWORD"],
)


def load_image(image_id: int, image_path: str) -> Image.Image:
    """Load an image, either from the disk or the nextcloud.

    Args:
    ----
        image_id (int): Unique identifier of the image
        image_path (str): Path to the image

    Returns:
    -------
        Image.Image: The resulting pillow image
    """
    # Check if the images is in the cache
    if os.path.exists(f"{CACHE_DIR}{image_id}.jpg"):
        image = Image.open(f"{CACHE_DIR}{image_id}.jpg")
        print("Cache hit")
    else:
        print("Cache miss")
        rgb_image = nextcloud_instance.files.download(image_path)
        image = Image.open(BytesIO(rgb_image))
        image.save(f"{CACHE_DIR}{image_id}.jpg", exif=image.getexif())
    return image
