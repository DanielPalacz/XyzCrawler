import unittest
from xyz import file_reader
from tests.base_test import BaseTest


class TestFileReader(unittest.TestCase):

    def test_init(self):
        file_reader.FileReader("example.txt")


class TestReading(BaseTest):

    def setUp(self) -> None:
        self.fr = file_reader.FileReader(self.get_fixture_path("urls.txt"))

    def test_readfile_return_type(self):
        self.assertIsInstance(self.fr.readfile(), set)

    def test_readfile_content(self):
        urls = self.fr.readfile()
        self.assertEqual(len(urls), 5, "There are not 4 links")
        self.assertTrue(all([u.startswith("http") for u in urls]))




# self jest slownikiem !!!
#

# negatywne
# --
