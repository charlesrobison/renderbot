import app.__init__ as app_init
from app.auth.forms import RegistrationForm
from app.models import User
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_testing import TestCase
import os
import pytest
import tempfile
import unittest

# to test, run: $python3 -m unittest discover
# or run: $python3 -m pytest tests.py
# NB: before testing, you must run:
# $export FLASK_APP=run.py
# $export FLASK_CONFIG=development
# contexts in flask: http://kronosapiens.github.io/blog/2014/08/14/understanding-contexts-in-flask.html
# https://pythonhosted.org/Flask-Testing/

class RenderbotTestCase(TestCase):
    # Testing setup
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    TESTING = True

    def create_app(self):
        app = app_init.create_app('testing')
        app.config['TESTING'] = True # not sure I need this
        return app

    def setUp(self):
        self.db = SQLAlchemy()

    def tearDown(self):
        self.db.session.remove()
        self.db.drop_all()

    # tests of individual pages

    def test_home_dir(self):
        c = self.app.test_client()
        rv = c.get('/')
        assert b'Renderbot' in rv.data

    # test database interaction
    def test_user_creation(self):
        user = User(email="test@test.com",
                    username="Test",
                    first_name="Tom",
                    last_name="Test",
                    password="test")
        self.db.session.add(user)
        assert user in self.db.session

    # test rendering of form submissions

# class RenderbotTestCase(unittest.TestCase):
#
#     def test_home_dir(self):
#         c = self.app.test_client()
#         rv = c.get('/')
#         assert b'Renderbot' in rv.data
#
#     def test_create_user(self):
#         c = self.app.test_client()
#         user = User(email="test@test.com",
#                     username="Test",
#                     first_name="Tom",
#                     last_name="Test",
#                     password="test")
#         self.db.session.add(user)
#         self.db.session.commit()
        # self.db.session.delete(user)

    #
    # def login(self, email, password):
    #     c = self.app.test_client()
    #     return c.post('/login', data=dict(
    #         email=email,
    #         password=password
    #     ), follow_redirects=True)
    #
    # def logout(self):
    #     return self.app.test_client().get('/logout', follow_redirects=True)
    #
    # def test_login(self):
    #     rv = self.login('test@test.com', 'test')
    #     assert b'Hi,' in rv.data
        # print(rv.data)
        # rv = self.login('bob', 'joe')
        # assert b'Invalid email address.' in rv.data
        # rv = self.login('test@test.com', 'fake')
        # print(rv.data)
        # assert b'Invalid email or password.' in rv.data

    # def test_logout(self):
    #     rv = self.logout()
    #     assert b'You have successfully been logged out.' in rv.data


    # def test_registration_form(self):
    #     # for problems here: http://stackoverflow.com/questions/17375340/testing-code-that-requires-a-flask-app-or-request-context
    #     with self.app.app_context():
    #         r = RegistrationForm()

if __name__ == '__main__':
    unittest.main()
