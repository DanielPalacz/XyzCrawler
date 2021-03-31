import unittest
import abc


class BaseTest(unittest.TestCase):
    DEPS = []
    RUNNING_PLUGINS = {}

    @classmethod
    def setUpClass(cls):
        print("HELLO")
        for dep in cls.DEPS:
            assert issubclass(dep, BaseDep)
            o = dep()
            o.start()
            cls.RUNNING_PLUGINS[dep.__name__] = o

    @classmethod
    def tearDownClass(cls):
        [dep.stop() for dep in cls.RUNNING_PLUGINS.values()]


class BaseDep(abc.ABC):
    @abc.abstractmethod
    def start(self): ...

    @abc.abstractmethod
    def stop(self): ...


class RedisDep(BaseDep):
    def start(self):
        # subpr
        # testing.redis
        print("start redis")

    def stop(self):
        # subpr
        print("stop redis")
        # self.server.stop()


class FlaskDep(BaseDep):
    def start(self):
        print("start flask")

    def stop(self):
        print("stop flask")


class DownloaderDep(BaseDep):
    def start(self):
        print("start downloader")

    def stop(self):
        print("stop downloader")


# testing.mongodb
class MongoDep(BaseDep):
    def start(self):
        print("start mongodb")

    def stop(self):
        print("stop mongodb")


class TestExample(BaseTest):
    DEPS = [RedisDep, FlaskDep, DownloaderDep, MongoDep]

    def test_aaa(self):
        assert 1 == 1

    def test_bbb(self):
        assert 1 == 1

    def test_ccc(self):
        assert 1 == 1


# if __name__ == "__main__":
#     p = FlaskDep()
#     p.stop()
