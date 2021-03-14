from file_reader import FileReader
from downloader import Downloader

import redis
import os


if __name__ == "__main__":
    # export XyzCrawlerInputPath=/home/danielp/PythonProjects/XyzCrawler/input;
    file_reader = FileReader(os.getenv("XyzCrawlerInputPath") + "/urls.txt")
    urls = file_reader.readfile()
    print(urls)

    # r = redis.Redis()
    # r.mset({"Croatia": "Zagreb", "Bahamas": "Nassau"})
    # print(r.get("Bahamas").decode("utf-8"))
    # poland = ["Cracow", "Warsaw", "Wroclaw"]
    # r.lpush("P1", *poland)
    # print(r.lpop("P1"))
    # print(r.lpop("P1"))

    #
    downloader = Downloader(urls)
    downloader.store_all_links_in_cache()
    #
    downloader.print_everything_from_cache()
