import unittest
from scripts.check_readme_badges import validate

class ReadmeBadgeTests(unittest.TestCase):
    def test_verified_badges(self):
        validate()
