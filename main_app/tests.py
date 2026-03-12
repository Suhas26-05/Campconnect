from types import SimpleNamespace

from django.test import SimpleTestCase
from django.urls import reverse

from .models import Session
from .views import redirect_user_by_role


class RedirectUserByRoleTests(SimpleTestCase):
    def test_hod_redirects_to_admin_home(self):
        response = redirect_user_by_role(SimpleNamespace(user_type='1'))
        self.assertEqual(response.url, reverse('admin_home'))

    def test_staff_redirects_to_staff_home(self):
        response = redirect_user_by_role(SimpleNamespace(user_type='2'))
        self.assertEqual(response.url, reverse('staff_home'))

    def test_student_redirects_to_student_home(self):
        response = redirect_user_by_role(SimpleNamespace(user_type='3'))
        self.assertEqual(response.url, reverse('student_home'))

    def test_parent_redirects_to_parent_home(self):
        response = redirect_user_by_role(SimpleNamespace(user_type='4'))
        self.assertEqual(response.url, reverse('parent_home'))

    def test_unknown_user_type_redirects_to_login(self):
        response = redirect_user_by_role(SimpleNamespace(user_type='9'))
        self.assertEqual(response.url, reverse('login_page'))


class SessionStringTests(SimpleTestCase):
    def test_session_uses_name_when_present(self):
        session = Session(name='21CSE-A')
        self.assertEqual(str(session), '21CSE-A')
