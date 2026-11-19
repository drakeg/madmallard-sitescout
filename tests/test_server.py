import unittest
from app.server import Handler


class HealthContractTest(unittest.TestCase):
    def test_handler_has_get(self):
        self.assertTrue(callable(Handler.do_GET))


if __name__ == "__main__":
    unittest.main()
