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
        self.user_musician = Profile(profile_id='2', email='bryan@ucl.ac.uk', username='bryan', profile_name=None,
                                     profile_description=None, location='London', rating=None, profile_image=None,
                                     block='0')
        self.user_venue = Profile(profile_id='1', email='vizon@ucl.ac.uk', username='vizon', profile_name=None,
                                  profile_description=None, location=None, rating=None, profile_image=None, block='0')
        self.venue = Venue(venue_id='1', venue_capacity=None, venue_type=None, profile_id='1')
        self.musician = Musician(musician_id='1', gender='1', profile_id='2', birthdate=None, availability=None,
                                 sc_id=None)
        self.user_venue.set_password('vizon')
        self.user_musician.set_password('bryan')
        db.session.add(self.user_musician)
        db.session.add(self.user_venue)
        db.session.add(self.venue)
        db.session.add(self.musician)
        db.session.commit()

    def tearDown(self):
        # Called at the end of every test
        db.session.remove()
        db.drop_all()

    def login(self, email, password):
        return self.client.post(
            '/login',
            data=dict(email=email, password=password),
            follow_redirects=True
        )

    def search(self, search_term, search_type, category):
        return self.client.post(
            '/search',
            data=dict(search_term=search_term, search_type=search_type, category=category),
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

    def setting(self, username, email, password, confirm, submit):
        return self.client.post(
            '/settings',
            data=dict(username=username, email=email, password=password, confirm=confirm, submit=submit),
            follow_redirects=True
        )

    def edit_profile(self, description, profile_name, location, genre, profile_image, birthdate, availability,
                     sc_id, submit):
        return self.client.post(
            '//edit_profile',
            data=dict(description=description, profile_name=profile_name, location=location, genre=genre,
                      profile_image=profile_image, birthdate=birthdate, availability=availability, sc_id=sc_id,
                      submit=submit),
            follow_redirects=True
        )

    # Provides the details for a musician.
    musician_data = dict(username='daniel', email='daniel@ucl.ac.uk',
                         password='daniel', confirm='daniel', option='m', submit='Register')
    existing_data = dict(username='vizon', email='vizon@ucl.ac.uk',
                         password='vizon', confirm='vizon', option='v', submit='Register')
    none_data = dict(username=None, email=None, password=None, confirm=None, option=None, submit='Register')

    unregistered_data = dict(username='dan', email='dan@ucl.ac.uk', password='dan', confirm='dan',
                             submit='Save')
    registered_data = dict(username='vizon', email='vizon@ucl.ac.uk', password='vizon', confirm='vizon',
                           submit='Save')

    new_profile_data = dict(description=None, profile_name='Gunawan', location='London', genre='Drum and Bass',
                            profile_image=None, birthdate=None, availability='1', sc_id=None, submit='Save')


class TestMain(BaseTestCase):

    def test_index_page_valid(self):
        """
        GIVEN a Flask application
        WHEN the '/' home page is requested (GET)
        THEN check the response is valid (200 status code)
        """
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_index_content_without_login(self):
        """
        GIVEN a Flask application
        WHEN the '/' home page is requested
        THEN check the response contains "Welcome!"
        """
        response = self.client.get('/')
        self.assertIn(b"Welcome to Musician's Network", response.data)

    def test_index_content_with_login(self):
        """
        GIVEN a Flask application
        WHEN the '/' home page is requested
        THEN check the response contains "Welcome!"
        """
        self.login(email='vizon@ucl.ac.uk', password='vizon')
        response = self.client.get('/')
        self.assertIn(b"Profiles", response.data)

    def test_about_musicians_page_valid(self):
        """
        GIVEN a Flask application
        WHEN the '/musicians' about musicians page is requested (GET)
        THEN check the response is valid (200 status code)
        """
        response = self.client.get('about/musicians')
        self.assertEqual(response.status_code, 200)

    def test_about_bands_page_valid(self):
        """
        GIVEN a Flask application
        WHEN the '/bands' about musicians page is requested (GET)
        THEN check the response is valid (200 status code)
        """
        response = self.client.get('about/bands')
        self.assertEqual(response.status_code, 200)

    def test_about_venues_page_valid(self):
        """
        GIVEN a Flask application
        WHEN the '/musicians' about musicians page is requested (GET)
        THEN check the response is valid (200 status code)
        """
        response = self.client.get('about/venues')
        self.assertEqual(response.status_code, 200)

    def test_profile_not_allowed_when_user_not_logged_in(self):
        """
        Test that view profile is inaccessible without login
        and redirects to login page and then the profile
        """
        target_url = url_for('main.index',account='venues')
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 302)

    def test_venue_displays_when_user_logged_in(self):
        """
            GIVEN a Flask application
            WHEN the 'venues' page is requested with a logged in user
            THEN check the response contains venues
            Note: This is an integration test rather than a unit test as it tests a sequence of interacting behaviours
        """
        self.login(email='bryan@ucl.ac.uk', password='bryan')
        response = self.client.get('/venues')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Venue genres", response.data)

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

    def test_search_name_when_user_logged_in(self):
        """
             GIVEN a Flask application
             WHEN the ‘Location' is selected and user searches existing location
             THEN the search results show profile card with searched location
         """
        self.login(email='vizon@ucl.ac.uk', password='vizon')
        response = self.client.post('/search', data=dict(
            search_term='bryan',
            search_type='Artists',
            category='Name',
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"'bryan' Artists Search Results", response.data)

    def test_search_location_when_user_logged_in(self):
        """
             GIVEN a Flask application
             WHEN the ‘Location' is selected and user searches existing location
             THEN the search results show profile card with searched location
         """
        self.login(email='vizon@ucl.ac.uk', password='vizon')
        response = self.client.post('/search', data=dict(
            search_term='London',
            search_type='Artists',
            category='Location',
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"bryan", response.data)

    def test_search_genre_when_user_logged_in(self):
        """
             GIVEN a Flask application
             WHEN the ‘Genre' is selected and user searches existing genre
             THEN the search results show profile card with searched genre
         """
        self.login(email='vizon@ucl.ac.uk', password='vizon')
        response = self.client.post('/search', data=dict(
            search_term='Drum and Bass',
            search_type='Artists',
            category='Genre',
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"'Drum and Bass' Artists Search Results", response.data)


class TestAuth(BaseTestCase):

    def test_registration_form_displays(self):
        """
           GIVEN a Flask application
           WHEN the '/register' s page is requested (GET)
           THEN check the response is valid (200 status code)
       """
        target_url = url_for('auth.register')
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Create an account!', response.data)

    def test_register_musician_success(self):
        """
               GIVEN a Flask application
               WHEN the new data is used to register (post)
               THEN check the response is valid (200 status code)
               """
        count = Profile.query.count()
        response = self.client.post(url_for('auth.register'), data=dict(
            username=self.musician_data.get('username'),
            email=self.musician_data.get('email'),
            password=self.musician_data.get('password'),
            confirm=self.musician_data.get('confirm'),
            option=self.musician_data.get('option'),
            submit=self.musician_data.get('submit')
        ), follow_redirects=True)
        count2 = Profile.query.count()
        self.assertEqual(count2 - count, 1)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Profiles', response.data)


    def test_register_musician_with_existing_username(self):
        """
               GIVEN a Flask application
               WHEN the registered data is used to register (post)
               THEN check the response is valid (200 status code)
               """
        count = Profile.query.count()
        response = self.client.post(url_for('auth.register'), data=dict(
            username=self.existing_data.get('username'),
            email=self.existing_data.get('email'),
            password=self.existing_data.get('password'),
            confirm=self.existing_data.get('confirm'),
            option=self.existing_data.get('option'),
            submit=self.existing_data.get('submit')
        ), follow_redirects=True)
        count2 = Profile.query.count()
        self.assertEqual(count2 - count, 0)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'An account is already registered for that username.', response.data)
        self.assertIn(b'An account is already registered for that email.', response.data)

    def test_register_musician_with_no_input(self):
        """
           GIVEN a Flask application
           WHEN the none is used to register (post)
           THEN check the response is valid (200 status code)
       """
        count = Profile.query.count()
        response = self.client.post(url_for('auth.register'), data=dict(
            username=self.none_data.get('username'),
            email=self.none_data.get('email'),
            password=self.none_data.get('password'),
            confirm=self.none_data.get('confirm'),
            option=self.none_data.get('option'),
            submit=self.none_data.get('submit')
        ), follow_redirects=True)
        count2 = Profile.query.count()
        self.assertEqual(count2 - count, 0)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'This field is required.', response.data)

    def test_login_succeeds_with_valid_details(self):
        """
           GIVEN a Flask application
           WHEN the registered data is used to login
           THEN check the response is valid
       """
        response = self.login(email='vizon@ucl.ac.uk', password='vizon')
        self.assertIn(b'Profiles', response.data)


    def test_login_fails_with_invalid_details(self):
        """
           GIVEN a Flask application
           WHEN the unregistered is used to login
           THEN check the response is valid
           """
        response = self.login(email='dil@ucl.com', password='dil')
        self.assertIn(b'Invalid email/password combination', response.data)

    def test_login_fails_with_no_details(self):
        """
           GIVEN a Flask application
           WHEN the none is used to login
           THEN check the response is valid
       """
        response = self.login(email=None, password=None)
        self.assertIn(b'This field is required.', response.data)

    def test_logout_valid(self):
        """
            GIVEN a Flask application
            WHEN the user has signed in and wants to logout
            THEN check the response is valid
        """
        self.login(email='vizon@ucl.ac.uk', password='vizon')
        redirect_url = url_for('main.index',account='musicians')
        response = self.client.get('/logout/')
        self.assertRedirects(response, redirect_url, b"Welcome to Musician's Network!.")

    def test_logout_invalid(self):
        """
           GIVEN a Flask application
           WHEN the user has not signed in and wants to logout
           THEN check the response is valid
       """
        redirect_url = url_for('auth.login')
        response = self.client.get('/logout/')
        self.assertRedirects(response, redirect_url, b"You must be logged in to view that page.")


class TestProf(BaseTestCase):

    def test_setting_form_displays(self):
        """
           GIVEN a Flask application
           WHEN the user has signed in and wants reset the setting
           THEN check the response is valid
       """
        self.login(email='vizon@ucl.ac.uk', password='vizon')
        target_url = url_for('prof.settings')
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Edit Personal Information', response.data)

    def test_setting_edit_success_with_unregistered_name(self):
        """
          GIVEN a Flask application
          WHEN the user has signed in and wants reset the username with an unregistered name
          THEN check the response is valid
        """
        self.login(email='vizon@ucl.ac.uk', password='vizon')
        count = Profile.query.count()
        response = self.client.post(url_for('prof.settings'), data=dict(
            username=self.unregistered_data.get('username'),
            email=self.unregistered_data.get('email'),
            password=self.unregistered_data.get('password'),
            confirm=self.unregistered_data.get('confirm'),
            submit=self.unregistered_data.get('submit')
        ), follow_redirects=True)
        count2 = Profile.query.count()
        self.assertEqual(count2 - count, 0)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Profiles', response.data)

    def test_setting_edit_unsuccess_with_registered_name(self):
        """
         GIVEN a Flask application
         WHEN the user has signed in and wants reset the username with a registered name
         THEN check the response is valid
       """
        self.login(email='vizon@ucl.ac.uk', password='vizon')
        count = Profile.query.count()
        response = self.client.post(url_for('prof.settings'), data=dict(
            username=self.registered_data.get('username'),
            email=self.registered_data.get('email'),
            password=self.registered_data.get('password'),
            confirm=self.registered_data.get('confirm'),
            submit=self.registered_data.get('submit')
        ), follow_redirects=True)
        count2 = Profile.query.count()
        self.assertEqual(count2 - count, 0)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'An account is already registered for that username.', response.data)

    def test_go_profile_without_login(self):
        """
            GIVEN a Flask application
            WHEN visitors wants to go to 'their profile'with out login
            THEN check the response is valid
       """
        response = self.client.get(url_for('prof.profile', username='bryan'))
        self.assertEqual(response.status_code, 302)

    def test_edit_profile_form_display_success_for_musician(self):
        """
             GIVEN a Flask application
             WHEN the user has signed in and wants to see the own profile
             THEN check the response is valid
       """
        self.login(email='bryan@ucl.ac.uk', password='bryan')
        target_url = url_for('prof.edit_profile')
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Birthdate', response.data)

    def test_edit_profile_form_display_success_for_venue(self):
        """
              GIVEN a Flask application
              WHEN the venue has signed in and wants to edit the profile
              THEN check the response is valid
        """
        self.login(email='vizon@ucl.ac.uk', password='vizon')
        target_url = url_for('prof.edit_profile')
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Venue Capacity', response.data)

    def test_edit_profile_with_data_success_for_musician(self):
        """
            GIVEN a Flask application
            WHEN the musician has signed in and wants to edit the profile with full information
            THEN check the response is valid
        """
        self.login(email='bryan@ucl.ac.uk', password='bryan')
        count = Profile.query.count()
        response = self.client.post(url_for('prof.edit_profile'), data=dict(
            description=self.new_profile_data.get('username'),
            profile_name=self.new_profile_data.get('email'),
            location=self.new_profile_data.get('password'),
            genre=self.new_profile_data.get('confirm'),
            profile_image=self.new_profile_data.get('submit'),
            birthdate=self.new_profile_data.get(' birthdate'),
            availability=self.new_profile_data.get('availability'),
            sc_id=self.new_profile_data.get('sc_id'),
            submit=self.new_profile_data.get('submit')
        ), follow_redirects=True)
        count2 = Profile.query.count()
        self.assertEqual(count2 - count, 0)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'', response.data)

    def test_edit_profile_without_data_success_for_musician(self):
        """
            GIVEN a Flask application
            WHEN the musician has signed in and wants to have a look in editing profile
            but doesnt want to change anything
            THEN check the response is valid
        """
        self.login(email='bryan@ucl.ac.uk', password='bryan')
        count = Profile.query.count()
        response = self.client.post(url_for('prof.edit_profile'), data=dict(
            description=None,
            profile_name=None,
            location=None,
            genre=None,
            profile_image=None,
            birthdate=None,
            availability=None,
            sc_id=None,
            submit=None
        ), follow_redirects=True)
        count2 = Profile.query.count()
        self.assertEqual(count2 - count, 0)
        self.assertEqual(response.status_code, 200)




if __name__ == '__main__':
    unittest.main()
