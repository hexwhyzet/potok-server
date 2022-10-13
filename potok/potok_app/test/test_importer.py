from django.test import TestCase

from potok_app.api import importer


class RedditGapPictureCase(TestCase):

    def test_stored_gap_picture(self):
        with open("files/reddit_gap_picture.png", "rb") as gap_picture:
            self.assertFalse(importer.downloaded_picture_is_not_reddit_gap_picture(gap_picture.read()),
                             "Downloaded reddit gap picture is not detected by function")

    def test_stored_not_gap_picture(self):
        with open("files/not_reddit_gap_picture.png", "rb") as not_gap_picture:
            self.assertTrue(importer.downloaded_picture_is_not_reddit_gap_picture(not_gap_picture.read()),
                            "Downloaded not reddit gap picture is not detected by function")
