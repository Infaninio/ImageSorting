import unittest
from unittest.mock import MagicMock
from PIL import Image as PILImage
from WebUI.Image import Custom_Image
from datetime import datetime

class TestCustomImage(unittest.TestCase):
    def setUp(self):
        self.test_image_path = "./test/test.jpg"
        self.custom_image = Custom_Image(self.test_image_path)

    def test_init(self):
        self.assertEqual(self.custom_image.path, self.test_image_path)
        self.assertIsNone(self.custom_image.location)
        self.assertIsNone(self.custom_image.date)

    def test_load_image_from_nextcloud(self):
        mock_instance = MagicMock()
        
        self.custom_image.nextcloud_instance = mock_instance
        with open("./test/test.jpg", "rb") as t_img:
            return_val = t_img.read()
        mock_instance.files.download.return_value = return_val

        self.custom_image._load_image_from_nextcloud()
        self.assertIsNotNone(self.custom_image.image)

    def test_get_location(self):
        self.custom_image.location = "Test Location"
        self.assertEqual(self.custom_image.get_location(), "Test Location")
        self.custom_image.location = None
        self.assertEqual(self.custom_image.get_location(), "Unknown location")

    def test_extract_date(self):
        mock_instance = MagicMock()
        
        self.custom_image.nextcloud_instance = mock_instance
        with open("./test/test.jpg", "rb") as t_img:
            return_val = t_img.read()
        mock_instance.files.download.return_value = return_val

        self.assertEqual(self.custom_image.get_date(), '2024-10-07 10:47:21')

    def test_get_date(self):
        self.custom_image.date = datetime.strptime('2023:01:01', '%Y:%m:%d')
        self.assertEqual(self.custom_image.get_date(), '2023-01-01 00:00:00')
        # Implement this test to check if the date is correctly formatted and returned as a string

if __name__ == '__main__':
    unittest.main()
