from file_reader import FileReader
from downloader import Downloader

import redis
import os

from datetime import date
from datetime import datetime
import logging


if __name__ == "__main__":
    # logging basicConfig

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    filelogname = "LogSession_" + str(date.today().strftime("%Y%m%d"))
    filelogname += "_" + str(datetime.now().hour) + str(datetime.now().minute) + ".log"
    # create file handler which logs even debug messages
    fh = logging.FileHandler(filelogname)
    fh.setLevel(logging.DEBUG)
    # create formatter and add it to the handler
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)

    file_reader = FileReader(os.getenv("XyzCrawlerInputPath") + "/urls.txt")
    urls = file_reader.readfile()
    print(urls)
    r_pool = redis.ConnectionPool(host="localhost", port=6379, db=0, max_connections=9)
    r_conn = redis.StrictRedis(connection_pool=r_pool)

    d = Downloader(r_conn)
    d.run(list(urls))
