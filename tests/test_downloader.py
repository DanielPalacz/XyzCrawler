import unittest
from xyz import downloader
from tests.fixtures.static_data import LINKS


class TestDownloaderInit(unittest.TestCase):

    def test_empty(self):
        downloader.Downloader()

    def test_parametrized(self):
        downloader.Downloader(LINKS)


class TestDownloader(unittest.TestCase):

    def setUp(self) -> None:
        self.downloader = downloader.Downloader(LINKS)

    def test___verify_link_correctness(self):
        tested_links = ["https://wikipedia.org", "www.wp.pl", "ahojajo"]
        expected_links = ["https://wikipedia.org", "www.wp.pl", ""]
        for i, tested_link in enumerate(tested_links):
            with self.subTest(tested_link):
                verified_link = self.downloader._Downloader__verify_link_correctness(tested_link)
                expected_link_value = tested_link
                self.assertEqual(verified_link, expected_links[i], "Link verification did not work correctly.")

    def test___clean_http_link(self):
        tested_links = ["https://wikipedia.org/", "//www.wp.pl", "https://www.reddit.com"]
        expected_links = ["https://wikipedia.org", "www.wp.pl", "https://www.reddit.com"]
        for i, tested_link in enumerate(tested_links):
            with self.subTest(tested_link):
                cleaned_link = self.downloader._Downloader__clean_http_link(tested_link)
                self.assertEqual(cleaned_link, expected_links[i], "Link cleaning did not work correctly.")

    def test___get_inherited_links(self):
        tested_link = "https://jsonplaceholder.typicode.com/guide/"
        expected_values = ["https://dev.to/typicode/what-s-new-in-husky-5-32g5",
                           "https://github.com/sponsors/typicode",
                           "https://blog.typicode.com",
                           "https://my-json-server.typicode.com",
                           "https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API",
                           "https://github.com/users/typicode/sponsorship",
                           "https://github.com/typicode"]

        inherited_links = self.downloader._Downloader__get_inherited_links(tested_link)
        for expected_link in expected_values:
            with self.subTest(expected_link):
                self.assertTrue(expected_link in inherited_links, "Expected link was not found.")
        self.assertEqual(len(inherited_links), len(expected_values), "Number of inherited links is not correct.")
