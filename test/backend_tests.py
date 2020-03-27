import unittest

from flask import url_for
from flask_testing import TestCase
from app import create_app, db

from app.models import Musician, Venue, Genre, Administrator, Profile, Profile_Genre


class BaseTestCase(TestCase):
    """Base test case."""

    def create_app(self):
        app = create_app('app.config.TestConfig')
        return app

    def setUp(self):
        # Called before every test
        db.create_all()

        # create test data
        self.user = Profile(profile_id='1', email='vizon@ucl.ac.uk', username='vizon', profile_name=None,
                             profile_description=None, location=None, rating=None, profile_image=None)
        self.venue = Venue(venue_id='1', venue_capacity=None, venue_type=None, profile_id='1')
        self.user.set_password('vizon')
        db.session.add(self.user)
        db.session.add(self.venue)
        db.session.commit()

    def tearDown(self):
        # Called at the end of every test
        db.session.remove()
        db.drop_all()

    def login(self, email, password):
        return self.client.post(
            '/login/',
            data=dict(email=email, password=password),
            follow_redirects=True
        )

    def logout(self):
        return self.client.get(
            '/logout/',
            follow_redirects=True
        )

    def register(self, username, email, password, confirm):
        return self.client.post(
            '/register/',
            data=dict(username=username, email=email, password=password, confirm=confirm),
            follow_redirects=True
        )

    # Provides the details for a musician.
    musician_data = dict(musician_id='1', email='cs123456@ucl.ac.uk',
                         password='test', confirm='test')

    # Provides the details for a venue.
    venue_data = dict(venue_id='1', email="ct123456@ucl.ac.uk", password="test", confirm="test")


class TestMain(BaseTestCase):

    def test_index_page_valid(self):
        """
        GIVEN a Flask application
        WHEN the '/' home page is requested (GET)
        THEN check the response is valid (200 status code)
        """
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_index_content(self):
        """
        GIVEN a Flask application
        WHEN the '/' home page is requested
        THEN check the response contains "Welcome!"
        """
        response = self.client.get('/')
        self.assertIn(b"Welcome to Musician's Network", response.data)

    def test_about_musicians_page_valid(self):
        """
        GIVEN a Flask application
        WHEN the '/musicians' about musicians page is requested (GET)
        THEN check the response is valid (200 status code)
        """
        response = self.client.get('/bands')
        self.assertEqual(response.status_code, 200)

    def test_profile_not_allowed_when_user_not_logged_in(self):
        """
        Test that view profile is inaccessible without login
        and redirects to login page and then the profile
        """
        target_url = url_for('main.venues')
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 302)

    def test_venue_displays_when_user_logged_in(self):
        """
            GIVEN a Flask application
            WHEN the 'venues' page is requested with a logged in user
            THEN check the response contains venues
            Note: This is an integration test rather than a unit test as it tests a sequence of interacting behaviours
        """
        self.login(email='vizon@ucl.ac.uk', password='vizon')
        response = self.client.get('/venues')
        self.assertEqual(response.status_code, 200)

    def test_search_redirects_to_login_when_user_not_logged_in(self):
        """
             GIVEN a Flask application
             WHEN the ‘/search' page is requested (GET) when the user is not logged in
             THEN the user is redirected to the login page
             Hint: try assertRedirects
             """
        redirect_url = url_for('auth.login')
        response = self.client.get('/search')
        self.assertRedirects(response, redirect_url, b'You must be logged in to view that page.')

        pass


class TestAuth(BaseTestCase):

    def test_registration_form_displays(self):
        target_url = url_for('auth.signup')
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Signup', response.data)

    def test_register_student_success(self):
        count = Student.query.count()
        response = self.client.post(url_for('auth.signup'), data=dict(
            email=self.student_data.get('email'),
            password=self.student_data.get('password'),
            name=self.student_data.get('name'),
            title=self.student_data.get('title'),
            role=self.student_data.get('role'),
            uni_id=self.student_data.get('uni_id'),
            confirm=self.student_data.get('confirm')
        ), follow_redirects=True)
        count2 = Student.query.count()
        self.assertEqual(count2 - count, 1)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome', response.data)

    def test_login_fails_with_invalid_details(self):
        response = self.login(email='john@john.com', password='Fred')
        self.assertIn(b'Invalid username or password', response.data)

    def test_login_succeeds_with_valid_details(self):
        response = self.login(email='cs1234567@ucl.ac.uk', password='cs1234567')
        self.assertIn(b'Welcome Ahmet Roth', response.data)


if __name__ == '__main__':
    unittest.main()