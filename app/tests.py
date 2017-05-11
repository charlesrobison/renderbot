# Imports
from flask import Flask
from flask import url_for
from flask_sqlalchemy import SQLAlchemy
from flask_testing import TestCase
from flask.ext.login import current_user
import os
import pytest
import tempfile
import unittest

# Local imports
import app.__init__ as app_init
from app.__init__ import db
from app.auth.forms import RegistrationForm
from app.models import User
from app.auth.uploads import file_validate as fv
from config import app_config
import app.auth.utilities as utilities


# to test, run: $python3 -m unittest discover
# or run: $python3 -m pytest tests.py
# NB: before testing, you must run:
# $export FLASK_APP=run.py
# $export FLASK_CONFIG=development
# contexts in flask: http://kronosapiens.github.io/blog/2014/08/14/understanding-contexts-in-flask.html
# https://pythonhosted.org/Flask-Testing/
# should add coverage report: https://pypi.python.org/pypi/pytest-cov/

class RenderbotTestCase(TestCase):
    # Testing setup
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    TESTING = True

    def create_app(self):
        app = app_init.create_app('testing')
        app.config['TESTING'] = True # not sure I need this
        return app

    def setUp(self):
        self.c = self.app.test_client()
        db.init_app(self.app)
        # db.create_all(app=app_init.create_app('testing'))
        db.create_all()
        self.first_user =  User(email="test@test.com",
                        username="Test",
                        first_name="Tom",
                        last_name="Test",
                        password="test")
        self.second_user =  User(email="tomtest@test.com",
                        username="TomTest",
                        first_name="Tom",
                        last_name="Test",
                        password="test")
        self.duplicate_user =  User(email="test@test.com",
                        username="Test2",
                        first_name="Tom2",
                        last_name="Test",
                        password="test")
        db.session.add(self.first_user)

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def login(self, email, password):
        return self.c.post('/login', data=dict(
            email=email,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.app.test_client().get('/logout', follow_redirects=True)

    # tests of individual pages

    def test_home_dir(self):
        rv = self.c.get('/')
        self.assertEqual(rv.status_code, 200)
        assert b'Renderbot' in rv.data, 'There\'s something wrong with your home page'

    # test that you can't access dashboard while not logged in
    def test_unverified_dashboard(self):
        target_url = url_for('home.dashboard')
        redirect_url = url_for('auth.login', next=url_for('home.dashboard'))
        rv = self.c.get(target_url)
        self.assertEqual(rv.status_code, 302)
        self.assertRedirects(rv, redirect_url)

    # test that you get the right error message when you try to access dashboard without being logged in
    def test_unverified_dashboard_message(self):
        rv = self.c.get('/dashboard', follow_redirects=True)
        assert b'You must be logged in to access this page.' in rv.data, 'You should not be able to access the dashboard without login'

    def test_registration_page(self):
        rv = self.c.get('/register')
        self.assertEqual(rv.status_code, 200)
        assert b'Register for an Account' in rv.data, 'Your registration page is broken'

    def test_login_page(self):
        rv = self.c.get('/login')
        self.assertEqual(rv.status_code, 200)
        assert b'Login to your account' in rv.data, 'The login page doesn\'t render properly'

    # unit tests

    # test that database is set up properly
    def test_db_set_up(self):
        assert self.first_user in db.session, 'Users are missing from your DB'

    # test database interaction
    def test_db_user_creation(self):
        db.session.add(self.second_user)
        assert self.second_user in db.session, 'Unable to add user to DB'

    def test_incorrect_user(self):
        assert self.duplicate_user not in db.session, 'Nonexistant users are popping up in your DB!'

    # test that only the right type of files are validated
    def test_txt_file_validate(self):
        with pytest.raises(TypeError, message='.txt file should not be upload-able'):
            mimetype = fv.detect_file_type('app/tests/test.txt')

    def test_csv_type(self):
        mimetype = fv.detect_file_type('app/tests/store_data.csv')
        assert mimetype == 'csv', 'File type detector can\'t recognize a CSV'

    def test_xlsx_type(self):
        mimetype = fv.detect_file_type('app/tests/store_data.xlsx')
        assert mimetype == 'xlsx', 'File type detector can\'t recognize an Excel sheet'

    def test_xlsx_type(self):
        mimetype = fv.detect_file_type('app/tests/store_data.tsv')
        assert mimetype == 'tsv', 'File type detector can\'t recognize a TSV'

    # test that only files with correct headers are validated
    def test_correct_headers(self):
        is_valid = fv.has_valid_headers('app/tests/store_data.csv', 'csv', ['Order Date', 'Customer Segment', 'Profit', 'Sales', 'Product Category'])
        assert is_valid == True, 'Your headers don\'t validate'
        is_valid = fv.has_valid_headers('app/tests/store_data.tsv', 'tsv', ['Order Date', 'Customer Segment', 'Profit', 'Sales', 'Product Category'])
        assert is_valid == True, 'Your headers don\'t validate'
        is_valid = fv.has_valid_headers('app/tests/store_data.xlsx', 'xlsx', ['Order Date', 'Customer Segment', 'Profit', 'Sales', 'Product Category'])
        assert is_valid == True, 'Your headers don\'t validate'

    def test_incorrect_header(self):
        is_valid = fv.has_valid_headers('app/tests/bad_data.csv', 'csv', ['Order Date', 'Customer Segment', 'Profit', 'Sales', 'Product Category'])
        assert is_valid == False, 'You\'re validating bad headers'
        is_valid = fv.has_valid_headers('app/tests/bad_data.tsv', 'tsv', ['Order Date', 'Customer Segment', 'Profit', 'Sales', 'Product Category'])
        assert is_valid == False, 'You\'re validating bad headers'
        is_valid = fv.has_valid_headers('app/tests/bad_data.xlsx', 'xlsx', ['Order Date', 'Customer Segment', 'Profit', 'Sales', 'Product Category'])
        assert is_valid == False, 'You\'re validating bad headers'

    # test that df creation works
    def test_df_creation(self):
        df = utilities.create_df('app/tests/store_data.csv', 'csv')
        headers = ['Row ID', 'Order Priority', 'Discount', 'Unit Price', 'Shipping Cost', 'Customer ID', 'Customer Name', 'Ship Mode', 'Customer Segment', 'Product Category', 'Product Sub-Category', 'Product Container', 'Product Name', 'Product Base Margin', 'Country', 'Region', 'State or Province', 'City', 'Postal Code', 'Order Date', 'Ship Date', 'Profit', 'Quantity ordered new', 'Sales', 'Order ID']
        assert df.columns.values.tolist() == headers, 'Cannot convert file to dataframe'

    # test that creating sorted df works
    def test_sorted_df(self):
        df = utilities.create_df_with_parse_date('app/tests/store_data.csv', 'csv', 'Ship Date')
        self.assertEqual(df.iloc[0][0], 24225, 'You\'re not sorting your dataframe properly.')

if __name__ == '__main__':
    unittest.main()
