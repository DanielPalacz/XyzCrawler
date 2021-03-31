import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

import logging


class Downloader:
    STOP_FLAG = False
    SUPPORTED_PROTOCOLS = ["https", "http"]
    SUPPORTED_CONTENT_TYPES = ["text/html"]
    DOWNLOAD_QUEUE = "queue:download"

    def __init__(self, redis_conn, *, headers: dict = None):
        self.redis_conn = redis_conn
        headers = headers if headers is not None else {}
        self.session = requests.Session()
        self.session.headers.update(headers)
        self.logger = logging.getLogger()
        self.logger.debug("Downloader object was initiated.")

    def _download(self, url):
        self.logger.debug("Get requests`s response object for url: %s", url)
        response = self._fetch(url)
        # print(response, response.url, response.headers, response.elapsed, response.status_code, response.is_redirect)

        if response and response.ok:
            content_type = response.headers.get("content-type", "")

            if any([1 if elem in content_type else 0 for elem in self.SUPPORTED_CONTENT_TYPES]):
                urls = self._extract(response.url, response.text)
                self._enqueue_urls(urls)
            else:
                self.logger.debug("The url: '%s' has content type: %s which is not supported", url, content_type)
        else:
            self.logger.debug("The given url could not be downloaded due to http code: %s", response.status_code)

    def _fetch(self, url):
        self.logger.info(f"Fetching the given url: {url}")
        try:
            return self.session.get(url, allow_redirects=True)
        except requests.RequestException as e:
            return None

    def _extract(self, baseurl, text):
        soup = BeautifulSoup(text, "html.parser")
        links = soup.find_all("a")
        hrefs = [link.get("href") for link in links]
        results = [urljoin(baseurl, link) for link in hrefs]
        self.logger.debug("Extracting links from the given url: %s", baseurl)
        return results

    def _enqueue_urls(self, urls: list):
        if urls:
            url_len = len(urls)
            self.redis_conn.lpush(self.DOWNLOAD_QUEUE, *urls)
            self.logger.info("Enqueue to Redis (newly extracted %d urls)", url_len)

    def run(self, urls: list = None):
        urls = urls if urls is not None else []
        self.logger.info("Downloader was started (initially with %s)", urls)
        for url in urls:
            self._download(url)
        while not self.STOP_FLAG:
            result = self.redis_conn.brpop(self.DOWNLOAD_QUEUE, timeout=1)
            if result:
                q, url = result
                self.logger.debug("Previously extracted url was loaded from Redis queue (url: %s)", url.decode())
                self._download(url.decode())
                self.logger.debug("Url: %s", url.decode())
                self.logger.debug("Previously extracted url was parsed for new url links (url: %s)", url.decode())


if __name__ == "__main__":
    # to learn:
    # -- import typing ... sequence
    pass
