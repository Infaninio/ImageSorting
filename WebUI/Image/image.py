import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

from PIL import Image
from PIL.ExifTags import IFD, TAGS
from pillow_heif import register_heif_opener
from typeguard import typechecked

from ..caching import load_image

register_heif_opener()


class Custom_Image:
    """Class for images stored on Nextcloud."""

    def __init__(self, image_id: int, path: str, location: Optional[str] = None, date: Optional[datetime] = None):
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
        self.image: Optional[Image.Image] = None
        self.id: int = image_id

    def _load_image(self):
        self.image = load_image(image_id=self.id, image_path=self.path)
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

    def get_image(self, image_size: Optional[Tuple[int, int]] = None) -> Image.Image:
        """Load and return the image, applying orientation if needed."""
        if not self.image:
            self._load_image()
        if image_size:
            img = self.image.copy()
            img.thumbnail(image_size)
            return img

        return self.image

    @property
    def name(self):
        return Path(self.path).name

    def get_preview(self):
        """Get a lightweight preview thumbnail without loading the full image into memory."""
        # Create thumbnail directly from file without loading full image
        import os

        from ..caching import CACHE_DIR

        # Try to use cached thumbnail first
        preview_cache_path = f"{CACHE_DIR}preview_{self.id}.jpg"
        if os.path.exists(preview_cache_path):
            return Image.open(preview_cache_path)

        # Load image for thumbnail creation, but don't keep it
        if self.image is not None:
            img = self.image.copy()
        elif os.path.exists(f"{CACHE_DIR}{self.id}.jpg"):
            img = Image.open(f"{CACHE_DIR}{self.id}.jpg")
        else:
            img = Image.open(self.path)

        # Create thumbnail and save to cache
        img.thumbnail([256, 256])  # Smaller preview to save memory
        img_copy = img.copy()

        # Save preview cache
        try:
            img_copy.save(preview_cache_path, format="JPEG", quality=85, optimize=True)
        except Exception as e:
            logging.warning(f"Could not save preview cache: {e}")

        # Close the original if it was opened fresh
        if self.image is None:
            img.close()

        return img_copy

    def get_dimensions(self) -> Tuple[int, int]:
        """Get image dimensions without loading the full image into memory.

        PIL lazily loads images - only reading the header for dimensions.

        Returns
        -------
            Tuple[int, int]: (width, height) of the image
        """
        # Use PIL's lazy loading to get dimensions without loading full image
        if self.image is not None:
            return self.image.size

        # Load just to get dimensions - PIL only reads header for size
        import os

        from ..caching import CACHE_DIR

        try:
            if os.path.exists(f"{CACHE_DIR}{self.id}.jpg"):
                img = Image.open(f"{CACHE_DIR}{self.id}.jpg")
                size = img.size
                img.close()  # Close immediately after getting size
                return size
            else:
                # Load image lazily to get dimensions - only header is read
                img = Image.open(self.path)
                size = img.size
                img.close()  # Close immediately after getting size
                return size
        except Exception as e:
            logging.warning(f"Error getting dimensions for {self.path}: {e}")
            # Fallback to default aspect ratio if we can't read dimensions
            return (1920, 1080)  # Default 16:9 ratio

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
                if TAGS.get(tag, None) == "DateTimeOriginal":  # Assuming the date is stored as DateTimeOriginal
                    return datetime.strptime(value, "%Y:%m:%d %H:%M:%S")

        raise ValueError("Could not read date from Exif Data")

    @typechecked
    def get_date(self) -> datetime:
        if self.date is not None:
            return self.date
        if self.image is None:
            self._load_image()

        try:
            self.date = self._extract_date(self.image)
        except ValueError:
            logging.warning(f"Could not read data from File {self.path}")
            return datetime.today()

        return self.date
