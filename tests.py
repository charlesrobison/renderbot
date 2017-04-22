import app.__init__
import os
import pytest
import tempfile
import unittest

# to test, run: $python3 -m unittest discover
# or run: $python3 -m pytest tests.py

class RenderbotTestCase(unittest.TestCase):
    def setUp(self):
        self.config_name = os.getenv('FLASK_CONFIG')
        self.app = app.__init__.create_app(self.config_name)
        self.SQLALCHEMY_TRACK_MODIFICATION = False

    def test_empty_db(self):
        rv = self.app.get('/')

if __name__ == '__main__':
    unittest.main()
