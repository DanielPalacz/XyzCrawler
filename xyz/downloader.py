import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin


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

    def _download(self, url):
        # 1.
        # get requests`s response object
        response = self._fetch(url)
        # print(response, response.url, response.headers, response.elapsed, response.status_code, response.is_redirect)
        # 2.
        # check if response and response.ok are True
        if response and response.ok:
            content_type = response.headers.get("content-type", "")

            if any([1 if elem in content_type else 0 for elem in self.SUPPORTED_CONTENT_TYPES]):
                urls = self._extract(response.url, response.text)
                self._enqueue_urls(urls)
            else:
                print(f"The url: {url}`s content type: ?? {content_type} ?? is not supported by application. ")
        else:
            print("The given url could not be downloaded due to http code:", response.status_code)

    def _fetch(self, url):
        try:
            return self.session.get(url, allow_redirects=True)
        except requests.RequestException as e:
            return None

    def _extract(self, baseurl, text):
        soup = BeautifulSoup(text, "html.parser")
        links = soup.find_all("a")
        hrefs = [link.get("href") for link in links]
        results = [urljoin(baseurl, link) for link in hrefs]
        print(results)
        return results

    def _enqueue_urls(self, urls: list):
        if urls:
            self.redis_conn.lpush(self.DOWNLOAD_QUEUE, *urls)

    def run(self, urls: list):
        for url in urls:
            self._download(url)
        while not self.STOP_FLAG:
            result = self.redis_conn.brpop(self.DOWNLOAD_QUEUE, timeout=1)
            if result:
                queue_name, url = result
                self._download(url.decode("utf-8"))


if __name__ == "__main__":
    import redis_connection
    r = redis_connection.RedisConnection()
    r_conn = r.get_connection()
    d = Downloader(r_conn)
    d.download("https://www.reddit.com")
