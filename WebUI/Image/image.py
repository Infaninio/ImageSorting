import logging
from datetime import datetime
from typing import Optional, Tuple

from caching import load_image
from PIL import Image
from PIL.ExifTags import IFD, TAGS
from pillow_heif import register_heif_opener
from typeguard import typechecked

register_heif_opener()


class Custom_Image:
    """Class for images stored on Nextcloud."""

    def __init__(self, image_id: int, path: str, location: Optional[str] = None, date: Optional[str] = None):
        """Represent a custom image with metadata and functionality to interact with Nextcloud.

        Args:
        ----
            image_id (int): Unique identifier of the database
            path (str): Path to the file on Nextcloud
            location (str, optional): Location of the image. Defaults to None.
            date (str, optional): Date of the image when taken. Defaults to None.
        """
        self.path: str = path
        self.location: Optional[str] = location
        self.date: Optional[datetime] = date
        self.image: Optional[Image.ImageFile.ImageFile] = None
        self.id: int = image_id

    def _load_image_from_nextcloud(self):
        self.image = load_image(self.id, self.path)
        self.image = self._apply_orientation(self.image)

    def _apply_orientation(self, img: Image.Image) -> Image.Image:
        """Correct image orientation based on EXIF data."""
        try:
            exif = img.getexif()
            orientation_tag = next(tag for tag, name in TAGS.items() if name == "Orientation")
            orientation = exif.get(orientation_tag, 1)  # Default to normal orientation (1)

            # Apply transformations based on the orientation value
            if orientation == 3:  # 180 degrees
                img = img.rotate(180, expand=True)
            elif orientation == 6:  # 90 degrees clockwise
                img = img.rotate(270, expand=True)
            elif orientation == 8:  # 90 degrees counterclockwise
                img = img.rotate(90, expand=True)

        except (AttributeError, KeyError, ValueError):
            logging.warning("Could not determine orientation from EXIF data. Returning original image.")

        return img

    def get_image(self, image_size: Optional[Tuple[int, int]] = None):
        """Load and return the image, applying orientation if needed."""
        if not self.image:
            self._load_image_from_nextcloud()
        if image_size:
            img = self.image.copy()
            img.thumbnail(image_size)
            return img

        return self.image

    def get_preview(self):
        img = self.get_image().copy()
        img.thumbnail([512, 512])
        return img

    def get_location(self) -> str:
        if self.location:
            return str(self.location)
        else:
            return "Unknown location"

    @staticmethod
    @typechecked
    def _extract_date(img: Image.Image) -> Optional[datetime]:
        """Read the dat of the photo from exif metadata of the image."""
        exif_info = img.getexif().get_ifd(IFD.Exif)
        if exif_info:
            for tag, value in exif_info.items():
                if TAGS[tag] == "DateTimeOriginal":  # Assuming the date is stored as DateTimeOriginal
                    return datetime.strptime(value, "%Y:%m:%d %H:%M:%S")

        raise ValueError("Could not read date from Exif Data")

    @typechecked
    def get_date(self) -> datetime:
        if self.date is not None:
            return self.date
        if self.image is None:
            self._load_image_from_nextcloud()

        try:
            self.date = self._extract_date(self.image)
        except ValueError:
            logging.warning(f"Could not read data from File {self.path}")
            return datetime.today()

        return self.date
