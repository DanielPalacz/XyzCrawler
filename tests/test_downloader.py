import unittest
from xyz import downloader
from tests.base_test import BaseTest, RedisMixin, WebAppTest

import redis
import requests
import requests_mock

import signal


class TestDownloaderInit(BaseTest, RedisMixin):

    @classmethod
    def setUpClass(cls) -> None:
        super().setup_redis()

    @classmethod
    def tearDownClass(cls) -> None:
        super().stop_redis()

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
            self.assertEqual(sorted(extracted_links), sorted(expected_links), "Extracted links aren`t correct.")


class TestFull(BaseTest, RedisMixin):
    # class TestFull(testtools.TestCase, BaseTest, RedisMixin):

    @classmethod
    def setUpClass(cls) -> None:
        super().setup_redis()

    @classmethod
    def tearDownClass(cls) -> None:
        super().stop_redis()

    def setUp(self):
        # super(TestFull, self).setUp()
        redis_connection = super().get_redis_connection()
        self.downloader = downloader.Downloader(redis_connection)
        # self.requests_mock = self.useFixture(fixture.Fixture())
        # self.requests_mock.register_uri('GET', self.TEST_URL, text='respA')

    def tearDown(self):
        # super(TestFull, self).tearDown()
        self.downloader.redis_conn.delete(self.downloader.DOWNLOAD_QUEUE)

    def test__enqueue_urls(self):
        data = ["a", "b", "c"]
        self.downloader._enqueue_urls(data)
        for elem in data[-1::-1]:
            with self.subTest(elem):
                popped_elem = self.downloader.redis_conn.lpop(self.downloader.DOWNLOAD_QUEUE).decode("utf-8")
                self.assertEqual(popped_elem, elem, "Incorrect element was stored.")

    def test__download(self):
        expected_links = [
            'http://test.com/', 'http://test.com/#top', 'http://test.com/subdir', "https://my-json-server.typicode.com",
            'https://pypi.org/project/requests-mock/', 'http://test.com/tmp', 'http://otherlink']

        with requests_mock.Mocker() as m:
            with open(self.get_fixture_path("localtest.html")) as localhtml:
                url = "http://test.com/"
                m.register_uri("GET", url=url, text=localhtml.read(), headers={"content-type": "text/html"})

                self.downloader._download(url)
                err = "Incorrect number of links were collected"
                self.assertEqual(
                    self.downloader.redis_conn.llen(self.downloader.DOWNLOAD_QUEUE), len(expected_links), err)

                while elem := self.downloader.redis_conn.lpop(self.downloader.DOWNLOAD_QUEUE):
                    popped_elem = elem.decode("utf-8")
                    with self.subTest(popped_elem):
                        self.assertTrue(popped_elem in expected_links, "The link taken from Redis was not expected")

    def test_run(self):

        def set_stop_flag(signum, frame):
            self.downloader.STOP_FLAG = True

        expected_links = ['http://test.com/', 'http://test.com/#top', 'http://test.com/subdir']

        with requests_mock.Mocker() as m:
            import re
            matcher = re.compile(url)

            with open(self.get_fixture_path("limitedhtml")) as limitedhtml:
                url = "http://test.com/"
                urls = [url]
                m.register_uri("GET", url=matcher, text=limitedhtml.read(), headers={"content-type": "text/html"})
                # Register the alarm signal with our handler
                signal.signal(signal.SIGALRM, set_stop_flag)
                # Set the alarm after 1 second -> self.downloader.STOP_FLAG = True
                signal.alarm(1)
                self.downloader.run(urls)

                while stored_url_bin := self.downloader.redis_conn.lpop(self.downloader.DOWNLOAD_QUEUE):
                    stored_url = stored_url_bin.decode("utf-8")
                    err = f"Incorrect link was extracted: {stored_url}"
                    self.assertTrue(stored_url in expected_links, err)

    def test_runner(self):

        def set_stop_flag(signum, frame):
            self.downloader.STOP_FLAG = True

        # Register the alarm signal with our handler
        signal.signal(signal.SIGALRM, set_stop_flag)

        with requests_mock.Mocker() as m:
            url_A = "http://test/A"
            url_B = "http://test/B"
            content_A = self.get_fixture_text("A.html")
            m.register_uri("GET", url=url_A, text=content_A, headers={"content-type": "text/html"})
            m.register_uri("GET", url=url_B, text="B_HTML", headers={"content-type": "text/html"})

            # Set the alarm after 1 second -> self.downloader.STOP_FLAG = True
            signal.alarm(1)
            self.downloader.run([url_A])

            self.assertEqual(m.call_count, 2)
            self.assertEqual(self.downloader.redis_conn.llen(self.downloader.DOWNLOAD_QUEUE), 0)


class TestFullWithWebApp(WebAppTest):

    def test_runner_with_webapp(self):
        url = "http://127.0.0.1:5678/A"
        # self.downloader.redis_conn.lpush(self.downloader.DOWNLOAD_QUEUE, url)
        self.downloader._enqueue_urls([url])
        signal.alarm(1)
        self.downloader.run()
        self.assertEqual(self.downloader.redis_conn.llen(self.downloader.DOWNLOAD_QUEUE), 0)
