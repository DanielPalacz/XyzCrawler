from file_reader import FileReader
from downloader import Downloader
from redis_connection import RedisConnection

import os


if __name__ == "__main__":
    file_reader = FileReader(os.getenv("XyzCrawlerInputPath") + "/urls.txt")
    urls = file_reader.readfile()
    print(urls)
    r = RedisConnection()
    r_conn = r.get_connection()

    d = Downloader(r_conn)
    for url in urls:
        d.download(url)
