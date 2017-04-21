import unittest
import pytest

class TestTest(unittest.TestCase):
    def test_arithmetic(self):
        self.assertEqual(2 + 2, 4)


if __name__ == '__main__':
    unittest.main()
