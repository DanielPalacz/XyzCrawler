import unittest
from xyz import downloader
from tests.base_test import BaseTest, RedisMixin
from tests.fixtures.static_data import LINKS, LOCAL_HTTP_SERVER
import requests
import requests_mock


class TestDownloaderInit(BaseTest, RedisMixin):

    @classmethod
    def setUpClass(cls) -> None:
        super().setup_redis()

    @classmethod
    def tearDownClass(cls) -> None:
        super().stop_redis()

    def setUp(self) -> None:
        redis_connection = super().get_redis_connection()
        self.downloader = downloader.Downloader(redis_connection)

    def tearDown(self):
        del self.downloader

    def test_session_defaults(self):
        d = self.downloader
        self.assertIn("python-requests", d.session.headers["User-agent"], "User-agent Header value was not correct.")

    def test_session_headers(self):
        d = downloader.Downloader(None, headers={"User-agent": "MyDownloader"})
        self.assertEqual(d.session.headers["User-agent"], "MyDownloader", "User-agent Header value was not correct.")


class TestDownloaderOperations(BaseTest):

    def setUp(self) -> None:
        self.downloader = downloader.Downloader(None)

    def tearDown(self):
        del self.downloader

    def test__fetch(self):
        with requests_mock.Mocker() as m:
            m.get("http://test.com", text="mocked test.com website")
            self.assertIsInstance(
                self.downloader._fetch("http://test.com"), requests.Response, "Incorrect object type returned.")
            self.assertIsNone(
                self.downloader._fetch("incorrect_url"), "Loading url failure was not handled correctly.")

    def test__extract(self):
        expected_links = [
            'http://test.com', 'http://test.com#top', 'http://test.com/subdir', "https://my-json-server.typicode.com",
            'https://pypi.org/project/requests-mock/', 'http://test.com/tmp', 'http://otherlink']

        with open(self.get_fixture_path("localtest.html")) as localhtml:
            extracted_links = self.downloader._extract("http://test.com", localhtml.read())
            for extracted_link in extracted_links:
                with self.subTest(extracted_link):
                    self.assertTrue(extracted_link in expected_links, "Expected link was not found.")
                self.assertEqual(len(extracted_links), len(expected_links), "Number of extracted links isn`t correct.")
