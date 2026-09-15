from django.test import TestCase
from django.urls import reverse

from Apps.accounts.models import User


class AdminLoginTests(TestCase):
    url = reverse("v1:accounts:admin-login")

    @classmethod
    def setUpTestData(cls):
        User.objects.create_user(email="admin@madperfume.com", password="secret-pass-1", full_name="Admin", is_staff=True)
        User.objects.create_user(email="customer@madperfume.com", password="secret-pass-1", full_name="Customer")

    def login(self, email, password="secret-pass-1"):
        return self.client.post(self.url, {"email": email, "password": password}, content_type="application/json")

    def test_admin_gets_tokens(self):
        # user lookup, last_login update, outstanding refresh token insert
        with self.assertNumQueries(3):
            response = self.login("admin@madperfume.com")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(response.json()), {"access", "refresh"})

    def test_wrong_password_rejected(self):
        self.assertEqual(self.login("admin@madperfume.com", "wrong").status_code, 401)

    def test_non_staff_rejected(self):
        self.assertEqual(self.login("customer@madperfume.com").status_code, 401)
