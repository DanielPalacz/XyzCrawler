import unittest
import os


class BaseTest(unittest.TestCase):

    ROOT_DIR = os.path.dirname(__file__)

    def get_fixture_path(self, filename):
        return os.path.join(self.ROOT_DIR, "fixtures", filename)
