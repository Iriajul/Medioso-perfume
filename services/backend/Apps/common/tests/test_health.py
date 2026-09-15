from django.test import TestCase
from django.urls import reverse


class HealthCheckTests(TestCase):
    def test_health_reports_ok(self):
        response = self.client.get(reverse("v1:common:health"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")
