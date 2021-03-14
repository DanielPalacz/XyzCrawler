import requests
import redis
from bs4 import BeautifulSoup


class Downloader:

    def __init__(self, list_with_urls: list = list()):
        self.links = {url: 0 for url in list_with_urls}
        self.cache = redis.Redis(host='localhost', port=6379, db=0)

    @staticmethod
    def __verify_link_correctness(url: str) -> str:
        if url.startswith("www.") or url.startswith("http"):
            pass
        else:
            url = ""
        return url

    @staticmethod
    def __clean_http_link(url: str) -> str:
        if url.startswith("//www."):
            url = url[2:]
        if url.endswith("/"):
            url = url[:-1]
        return url

    def __get_inherited_links(self, url) -> list:
        req = requests.get(url)
        soup = BeautifulSoup(req.text, "html.parser")

        inherited_links = list()

        for link_elem in soup.findAll("a"):
            inherited_link = link_elem.get('href')
            if inherited_link:
                inherited_link = self.__clean_http_link(inherited_link)
                inherited_link = self.__verify_link_correctness(inherited_link)
                inherited_links.append(inherited_link)

        return [inh_link for inh_link in inherited_links if bool(inh_link)]

    def __store_links_list_in_cache(self, url, link_lists):
        if len(link_lists):
            self.cache.lpush(url, *link_lists)

    def store_all_links_in_cache(self):
        for link in self.links.keys():
            inherited_links = []
            try:
                inherited_links = self.__get_inherited_links(link)
                self.links[link] += 1
            except Exception as e:
                print("Raised the following exception during links scrapping:", e)

            print("Storing in cache everything for list named:", link)
            print(inherited_links)
            self.__store_links_list_in_cache(link, inherited_links)

    def print_everything_from_cache(self):
        for link in self.links:
            while cached_value := self.cache.lpop(link):
                print(cached_value.decode("utf-8"))
