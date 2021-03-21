import unittest
from xyz import downloader
from tests.base_test import BaseTest, RedisMixin

import redis
import requests
import requests_mock


class TestDownloaderInit(BaseTest, RedisMixin):

    @classmethod
    def setUpClass(cls) -> None:
        super().setup_redis()

    @classmethod
    def tearDownClass(cls) -> None:
        super().stop_redis()
        print()

    def setUp(self):
        redis_connection = super().get_redis_connection()
        self.downloader = downloader.Downloader(redis_connection)

    def tearDown(self):
        del self.downloader

    def test_session_defaults(self):
        d = self.downloader
        self.assertIsInstance(self.downloader.redis_conn, redis.client.Redis, "Incorrect object type returned.")
        self.assertIn("python-requests", d.session.headers["User-agent"], "User-agent Header value was not correct.")

    def test_session_headers(self):
        d = downloader.Downloader(None, headers={"User-agent": "MyDownloader"})
        self.assertIsNone(d.redis_conn)
        self.assertEqual(d.session.headers["User-agent"], "MyDownloader", "User-agent Header value was not correct.")


class TestDownloaderOperations(BaseTest):

    @classmethod
    def tearDownClass(cls) -> None:
        print()

    def setUp(self):
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


class TestDownloaderRedis(BaseTest, RedisMixin):

    @classmethod
    def setUpClass(cls) -> None:
        super().setup_redis()

    @classmethod
    def tearDownClass(cls) -> None:
        super().stop_redis()
        print()

    def setUp(self):
        redis_connection = super().get_redis_connection()
        self.downloader = downloader.Downloader(redis_connection)

    def tearDown(self):
        del self.downloader

    def test__store(self):
        self.downloader.REDIS_CACHE_LIST = "TESTS_URL_TEMP_CACHE"
        data = ["a", "b", "c"]
        self.downloader._store(data)
        for elem in data[-1::-1]:
            with self.subTest(elem):
                popped_elem = self.downloader.redis_conn.lpop(self.downloader.REDIS_CACHE_LIST).decode("utf-8")
                self.assertEqual(popped_elem, elem, "Incorrect element was stored.")

    def test_download(self):
        expected_links = [
            'http://test.com/', 'http://test.com/#top', 'http://test.com/subdir', "https://my-json-server.typicode.com",
            'https://pypi.org/project/requests-mock/', 'http://test.com/tmp', 'http://otherlink']

        with requests_mock.Mocker() as m:
            with open(self.get_fixture_path("localtest.html")) as localhtml:
                url = "http://test.com/"
                m.register_uri("GET", url=url, text=localhtml.read(), headers={"content-type": "text/html"})

                self.downloader.download(url)
                popped_numbers = 0
                while elem := self.downloader.redis_conn.lpop(self.downloader.REDIS_CACHE_LIST):
                    popped_elem = elem.decode("utf-8")
                    popped_numbers += 1
                    with self.subTest(popped_elem):
                        self.assertTrue(popped_elem in expected_links, "The link taken from Redis was not expected")
                else:
                    self.assertTrue(popped_numbers == len(expected_links), "Incorrect number of links were collected")
