import unittest
from src.adapt import split

class TestSplit(unittest.TestCase):
    def test_split_returns_edge(self):
        self.assertEqual(split(1), 1)
