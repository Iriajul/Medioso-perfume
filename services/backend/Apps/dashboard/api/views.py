from django.db.models import Sum
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from Apps.accounts.models import User
from Apps.catalog.models import Product
from Apps.common.stats import count_trend
from Apps.loyalty.models import LoyaltyTransaction
from Apps.orders.models import Order


class DashboardView(APIView):
    """Admin dashboard overview."""

    permission_classes = [IsAdminUser]

    def get(self, request):
        total_customers, customers_trend = count_trend(User.objects.filter(is_staff=False))
        total_orders, orders_trend = count_trend(Order.objects.all())
        recent_orders = Order.objects.select_related("customer")[:4]
        activity = LoyaltyTransaction.objects.select_related("customer", "reward")[:5]

        return Response({
            "total_customers": total_customers,
            "customers_trend": customers_trend,
            "total_products": Product.objects.count(),
            "total_orders": total_orders,
            "orders_trend": orders_trend,
            "points_issued": LoyaltyTransaction.objects.filter(kind="earned").aggregate(total=Sum("points"))["total"] or 0,
            "recent_orders": [
                {"id": o.id, "number": o.number, "customer_name": o.customer.full_name, "status": o.status, "total": str(o.total)}
                for o in recent_orders
            ],
            "loyalty_activity": [
                {"id": t.id, "customer_name": t.customer.full_name, "kind": t.kind, "channel": t.channel,
                 "reward_name": t.reward.name if t.reward else None, "points": t.points}
                for t in activity
            ],
        })
