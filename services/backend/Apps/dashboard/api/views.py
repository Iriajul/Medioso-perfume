from datetime import timedelta

from django.db.models import Count, Q
from django.utils import timezone
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from Apps.accounts.models import User
from Apps.catalog.models import Product


def trend_percent(current, previous):
    """Change of the last 30 days vs the 30 days before, or None without a baseline."""
    return round((current - previous) / previous * 100) if previous else None


class DashboardView(APIView):
    """Admin dashboard overview. Order and loyalty figures are filled in
    as those apps land; until then they are zero / empty."""

    permission_classes = [IsAdminUser]

    def get(self, request):
        now = timezone.now()
        customers = User.objects.filter(is_staff=False).aggregate(
            total=Count("id"),
            current=Count("id", filter=Q(created_at__gte=now - timedelta(days=30))),
            previous=Count("id", filter=Q(created_at__gte=now - timedelta(days=60), created_at__lt=now - timedelta(days=30))),
        )
        return Response(
            {
                "total_customers": customers["total"],
                "customers_trend": trend_percent(customers["current"], customers["previous"]),
                "total_products": Product.objects.count(),
                "total_orders": 0,
                "orders_trend": None,
                "points_issued": 0,
                "recent_orders": [],
                "loyalty_activity": [],
            }
        )
