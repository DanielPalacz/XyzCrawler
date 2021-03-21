import unittest
import os
import testing.redis
import redis


class BaseTest(unittest.TestCase):

    # ENABLE_REDIS = False
    # ENABLE_SQLDB = False
    ROOT_DIR = os.path.dirname(__file__)

    def get_fixture_path(self, filename):
        return os.path.join(self.ROOT_DIR, "fixtures", filename)

    # @classmethod
    # def setUpClass(cls) -> None:
    #     if cls.ENABLE_REDIS:
    #         cls.redis_server = testing.redis.RedisServer()
    #         print("Staring redis server (BaseTest with RedisMixin inside: BaseTest.setUpClass).")
    #
    # @classmethod
    # def tearDownClass(cls) -> None:
    #     if cls.ENABLE_REDIS:
    #         cls.redis_server.stop()
    #         print("Stopping redis server (BaseTest with RedisMixin inside: BaseTest.tearDownClass).")


class RedisMixin:

    @classmethod
    def setup_redis(cls) -> None:
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
