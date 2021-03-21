import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin


class Downloader:
    SUPPORTED_PROTOCOLS = ["https", "http"]
    SUPPORTED_CONTENT_TYPES = ["text/html"]

    def __init__(self, redis_conn, *, headers: dict = None):
        self.redis_conn = redis_conn
        headers = headers if headers is not None else {}
        self.session = requests.Session()
        self.session.headers.update(headers)

    def download(self, url):
        # 1.
        # get requests`s response object
        response = self._fetch(url)
        # 2.
        # check if response and response.ok are True
        if response and response.ok:
            content_type = response.headers.get("content-type", "")
            if content_type in self.SUPPORTED_CONTENT_TYPES:
                urls = self._extract(response.url, response.text)
                break
            else:
                print(f"The url: {url}`s content type: {content_type} is not supported by application. ")
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
        return results


if __name__ == "__main__":
    d = Downloader(None)
    print(d.download())
