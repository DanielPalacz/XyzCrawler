import unittest


class BaseTest(unittest.TestCase):
    DEPS = []

    @classmethod
    def setUpClass(cls):
        ...

    @classmethod
    def tearDownClass(cls):
        ...


class TestExample(BaseTest):
    def test_me(self):
        assert 1 == 1
