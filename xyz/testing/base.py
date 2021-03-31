from xyz import downloader
from xyz.testing.flask import FlaskServer

import unittest
import os
import sys
import testing.redis
import redis
import signal
import logging


# logging.basicConfig(
#     # filename='example.log',
#     encoding='utf-8',
#     level=logging.DEBUG if int(os.environ.get("DEBUG", 0)) else logging.INFO
# )

class Loggable:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            logging.Formatter(
                "%(levelname)s %(asctime)s "
                "%(name)24s.%(funcName)-32s %(filename)s:%(lineno)s %(message)s")
        )
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
        self.logger.info("Initialized")


class BaseTest(unittest.TestCase, Loggable):
    # ENABLE_REDIS = False
    # ENABLE_SQLDB = False
    ROOT_DIR = os.path.dirname(__file__)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        Loggable.__init__(self)

    def get_fixture_path(self, filename):
        return os.path.join(self.ROOT_DIR, "../../tests/fixtures", filename)

    def get_fixture_text(self, filename):
        with open(self.get_fixture_path(filename)) as fixture_file:
            return fixture_file.read()

    # @classmethod
    # def setUpClass(cls) -> None:
    #     if cls.ENABLE_REDIS:
    #         cls.redis_server = testing.redis.RedisServer()
    #         print("Staring redis server (BaseTest with RedisMixin inside: BaseTest.setUpClass).")

    # @classmethod
    # def tearDownClass(cls) -> None:
    #     if cls.ENABLE_REDIS:
    #         cls.redis_server.stop()
    #         print("Stopping redis server (BaseTest with RedisMixin inside: BaseTest.tearDownClass).")


class RedisMixin(Loggable):

    @classmethod
    def start_redis(cls) -> None:
        cls.redis_server = testing.redis.RedisServer()
        print("[log]: Redis server started (RedisMixin.setupRedis) with the following params:", cls.redis_server.dsn())
        cls.redis_pool = redis.ConnectionPool(**cls.redis_server.dsn(), max_connections=10)
        print("[log]: Creating redis connection pool (RedisMixin.setupRedis).")

    @classmethod
    def stop_redis(cls) -> None:
        cls.redis_server.stop()
        print("[log]: Stopping redis server (RedisMixin.stopRedis).")

    @classmethod
    def get_redis_connection(cls):
        return redis.StrictRedis(connection_pool=cls.redis_pool)


class FlaskMixin(Loggable):
    @classmethod
    def start_flask(cls, *args, **kwargs):
        cls.flask_server = FlaskServer(*args, **kwargs)

    @classmethod
    def stop_flask(cls):
        cls.flask_server.stop()


class WebAppTest(BaseTest, RedisMixin):
    #

    @classmethod
    def setUpClass(cls) -> None:
        super().setup_redis()

    @classmethod
    def tearDownClass(cls) -> None:
        super().stop_redis()

    def setUp(self):
        def set_stop_flag(signum, frame):
            self.downloader.STOP_FLAG = True

        redis_connection = super().get_redis_connection()
        self.downloader = downloader.Downloader(redis_connection)
        # Register the alarm signal with our handler
        signal.signal(signal.SIGALRM, set_stop_flag)

    def tearDown(self):
        self.downloader.redis_conn.delete(self.downloader.DOWNLOAD_QUEUE)
