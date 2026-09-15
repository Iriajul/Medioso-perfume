from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework_simplejwt.tokens import AccessToken

from Apps.accounts.models import User


class DashboardTests(TestCase):
    url = reverse("v1:dashboard:overview")

    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_user(email="admin@madperfume.com", password="x", full_name="Admin", is_staff=True)
        now = timezone.now()
        # 3 customers in the last 30 days, 2 in the 30 days before, 1 older.
        for i, days_ago in enumerate([1, 5, 20, 35, 50, 90]):
            user = User.objects.create_user(email=f"c{i}@madperfume.com", password="x", full_name=f"Customer {i}")
            User.objects.filter(pk=user.pk).update(created_at=now - timedelta(days=days_ago))

    def get(self, user=None):
        headers = {"HTTP_AUTHORIZATION": f"Bearer {AccessToken.for_user(user)}"} if user else {}
        return self.client.get(self.url, **headers)

    def test_admin_overview(self):
        # auth user lookup + one aggregate query
        with self.assertNumQueries(2):
            response = self.get(self.admin)

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total_customers"], 6)
        self.assertEqual(data["customers_trend"], 50)  # 3 vs 2
        self.assertEqual(data["recent_orders"], [])

    def test_requires_admin(self):
        self.assertEqual(self.get().status_code, 401)
        self.assertEqual(self.get(User.objects.get(email="c0@madperfume.com")).status_code, 403)
