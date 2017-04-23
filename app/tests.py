import app.__init__
from app.auth.forms import RegistrationForm
import os
import pytest
import tempfile
import unittest

# to test, run: $python3 -m unittest discover
# or run: $python3 -m pytest tests.py
# contexts in flask: http://kronosapiens.github.io/blog/2014/08/14/understanding-contexts-in-flask.html

class RenderbotTestCase(unittest.TestCase):
    def setUp(self):
        self.config_name = os.getenv('FLASK_CONFIG')
        self.app = app.__init__.create_app(self.config_name)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.SQLALCHEMY_TRACK_MODIFICATION = False

    def test_empty_db(self):
        c = self.app.test_client()
        rv = c.get('/')

    def test_registration_form(self):
        # for problems here: http://stackoverflow.com/questions/17375340/testing-code-that-requires-a-flask-app-or-request-context
        with self.app.app_context():
            r = RegistrationForm()

if __name__ == '__main__':
    unittest.main()
