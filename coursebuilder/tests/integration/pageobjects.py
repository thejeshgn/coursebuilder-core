# Copyright 2013 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Page objects used in functional tests for Course Builder."""

__author__ = 'John Orr (jorr@google.com)'

from selenium.webdriver.common import by
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support import select
from selenium.webdriver.support import wait


class PageObject(object):
    """Superclass to hold shared logic used by page objects."""

    def __init__(self, tester):
        self._tester = tester

    def find_element_by_css_selector(self, selector):
        return self._tester.driver.find_element_by_css_selector(selector)

    def find_element_by_id(self, elt_id):
        return self._tester.driver.find_element_by_id(elt_id)

    def find_element_by_link_text(self, text):
        return self._tester.driver.find_element_by_link_text(text)

    def find_element_by_name(self, name):
        return self._tester.driver.find_element_by_name(name)

    def expect_status_message_to_be(self, value):
        wait.WebDriverWait(self._tester.driver, 15).until(
            ec.text_to_be_present_in_element(
                (by.By.ID, 'formStatusMessage'), value))


class EditorPageObject(PageObject):
    """Page object for pages which wait for the editor to finish loading."""

    def __init__(self, tester):
        super(EditorPageObject, self).__init__(tester)
        self.expect_status_message_to_be('Success.')

    def set_status(self, status):
        select.Select(self.find_element_by_name(
            'is_draft')).select_by_visible_text(status)
        return self


class RootPage(PageObject):
    """Page object to model the interactions with the root page."""

    def load(self, base_url):
        self._tester.driver.get(base_url + '/')
        return self

    def click_login(self):
        self.find_element_by_link_text('Login').click()
        return LoginPage(self._tester)

    def click_dashboard(self):
        self.find_element_by_link_text('Dashboard').click()
        return DashboardPage(self._tester)

    def click_admin(self):
        self.find_element_by_link_text('Admin').click()
        return AdminPage(self._tester)

    def click_announcements(self):
        self.find_element_by_link_text('Announcements').click()
        return AnnouncementsPage(self._tester)

    def click_register(self):
        self.find_element_by_link_text('Register').click()
        return RegisterPage(self._tester)


class RegisterPage(PageObject):
    """Page object to model the registration page."""

    def enroll(self, name):
        enroll = self.find_element_by_name('form01')
        enroll.send_keys(name)
        enroll.submit()
        return RegisterPage(self._tester)

    def verify_enrollment(self):
        self._tester.assertTrue(
            'Thank you for registering' in self.find_element_by_css_selector(
                'p.top_content').text)
        return self

    def click_course(self):
        self.find_element_by_link_text('Course').click()
        return RootPage(self._tester)


class AnnouncementsPage(PageObject):
    """Page object to model the announcements page."""

    def click_add_new(self):
        self.find_element_by_css_selector(
            '#gcb-add-announcement > button').click()
        return AnnouncementsEditorPage(self._tester)

    def verify_announcement(self, title=None, date=None, body=None):
        """Verify that the announcement has the given fields."""
        if title:
            self._tester.assertEquals(
                title, self._tester.driver.find_elements_by_css_selector(
                    'div.gcb-aside h2')[0].text)
        if date:
            self._tester.assertEquals(
                date, self._tester.driver.find_elements_by_css_selector(
                    'div.gcb-aside p')[0].text)
        if body:
            self._tester.assertEquals(
                body, self._tester.driver.find_elements_by_css_selector(
                    'div.gcb-aside p')[1].text)
        return self


class AnnouncementsEditorPage(EditorPageObject):
    """Page to model the announcements editor."""

    def enter_fields(self, title=None, date=None, body=None):
        """Enter title, date, and body into the announcement form."""
        if title:
            title_el = self.find_element_by_name('title')
            title_el.clear()
            title_el.send_keys(title)
        if date:
            date_el = self.find_element_by_name('date')
            date_el.clear()
            date_el.send_keys(date)
        if body:
            body_el = self.find_element_by_name('html')
            body_el.clear()
            body_el.send_keys(body)
        return self

    def save(self):
        self.find_element_by_link_text('Save').click()
        self.expect_status_message_to_be('Saved.')
        return self

    def close(self):
        self.find_element_by_link_text('Close').click()
        return AnnouncementsPage(self._tester)


class LoginPage(PageObject):
    """Page object to model the interactions with the login page."""

    def login(self, login, admin=False):
        email = self._tester.driver.find_element_by_id('email')
        email.clear()
        email.send_keys(login)
        if admin:
            self.find_element_by_id('admin').click()
        self.find_element_by_id('submit-login').click()
        return RootPage(self._tester)


class DashboardPage(PageObject):
    """Page object to model the interactions with the dashboard landing page."""

    def load(self, base_url, name):
        self._tester.driver.get('/'.join([base_url, name, 'dashboard']))
        return self

    def verify_read_only_course(self):
        self._tester.assertEquals(
            'Read-only course.',
            self.find_element_by_id('gcb-alerts-bar').text)
        return self

    def verify_not_publicly_available(self):
        self._tester.assertEquals(
            'The course is not publicly available.',
            self.find_element_by_id('gcb-alerts-bar').text)
        return self

    def click_add_unit(self):
        self.find_element_by_css_selector('#add_unit > button').click()
        return AddUnit(self._tester)

    def verify_course_outline_contains_unit(self, unit_title):
        self.find_element_by_link_text(unit_title)
        return self


class AddUnit(EditorPageObject):
    """Page object to model the dashboard's add unit editor."""

    def __init__(self, tester):
        super(AddUnit, self).__init__(tester)
        self.expect_status_message_to_be('New unit has been created and saved.')

    def set_title(self, title):
        title_el = self.find_element_by_name('title')
        title_el.clear()
        title_el.send_keys(title)
        return self

    def click_save_and_expect_unit_added(self):
        self.find_element_by_link_text('Save').click()
        self.expect_status_message_to_be('Saved.')
        return self

    def click_close(self):
        self.find_element_by_link_text('Close').click()
        return DashboardPage(self._tester)


class AdminPage(PageObject):
    """Page object to model the interactions with the admimn landing page."""

    def click_add_course(self):
        self.find_element_by_id('add_course').click()
        return AddCourseEditorPage(self._tester)

    def click_settings(self):
        self.find_element_by_link_text('Settings').click()
        return AdminSettingsPage(self._tester)


class AdminSettingsPage(PageObject):
    """Page object for the admin settings."""

    def click_override_admin_user_emails(self):
        self._tester.driver.find_elements_by_css_selector(
            'button.gcb-button')[0].click()
        return ConfigPropertyOverridePage(self._tester)

    def verify_admin_user_emails_contains(self, email):
        self._tester.assertTrue(
            email in self._tester.driver.find_elements_by_css_selector(
                'table.gcb-config tr')[1].find_elements_by_css_selector(
                    'td')[1].text)


class ConfigPropertyOverridePage(EditorPageObject):
    """Page object for the admin property override editor."""

    def set_value(self, value):
        self.find_element_by_name('value').send_keys(value)
        return self

    def click_save(self):
        self.find_element_by_link_text('Save').click()
        self.expect_status_message_to_be('Saved.')
        return self

    def click_close(self):
        self.find_element_by_link_text('Close').click()
        return AdminSettingsPage(self._tester)


class AddCourseEditorPage(EditorPageObject):
    """Page object for the dashboards' add course page."""

    def set_fields(self, name=None, title=None, email=None):
        """Populate the fields in the add course page."""
        name_el = self.find_element_by_name('name')
        title_el = self.find_element_by_name('title')
        email_el = self.find_element_by_name('admin_email')

        name_el.clear()
        title_el.clear()
        email_el.clear()

        if name:
            name_el.send_keys(name)
        if title:
            title_el.send_keys(title)
        if email:
            email_el.send_keys(email)

        return self

    def click_add_new_course_and_expect_course_added(self):
        self.find_element_by_link_text('Add New Course').click()
        self.expect_status_message_to_be('Added.')
        return self

    def click_close(self):
        self.find_element_by_link_text('Close').click()
        return AdminPage(self)