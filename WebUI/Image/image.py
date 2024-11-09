from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS, IFD
from io import BytesIO
from pillow_heif import register_heif_opener
from nc_py_api import Nextcloud
from typing import Optional
from typeguard import typechecked
import logging
import os 

register_heif_opener()

class Custom_Image:
    nextcloud_instance = Nextcloud(nextcloud_url="https://cloud.trauberg.de", nc_auth_user=os.environ["NEXTCLOUD_USER"], nc_auth_pass=os.environ["NEXTCLOUD_PASSWORD"])

    def __init__(self, path: str, location=None, date: Optional[str]=None):
        self.path: str = path
        self.location: Optional[str] = location
        self.date: Optional[datetime] = date
        self.image: Optional[Image.ImageFile.ImageFile] = None

    def _load_image_from_nextcloud(self):
        rgb_image = self.nextcloud_instance.files.download(self.path)
        self.image = Image.open(BytesIO(rgb_image))
    
    def get_image(self):
        if not self.image:
            self._load_image_from_nextcloud()
        
        return self.image
    
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
    def get_date(self) -> str:
        if self.date is not None:
            return str(self.date)
        if self.image is None:
            self._load_image_from_nextcloud()
        
        try:
            self.date = self._extract_date(self.image)
        except ValueError:
            logging.warning(f"Could not read data from File {self.path}")
            return ""

        return str(self.date)


    