from django.db.models import Avg, Prefetch, Q, Sum
from django.shortcuts import get_object_or_404
from rest_framework import mixins, serializers
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from Apps.accounts.models import User
from Apps.common.stats import money
from Apps.loyalty.models import LoyaltyTransaction
from Apps.loyalty.services import tier_for, tier_progress
from Apps.orders.models import Order, OrderItem


class CustomerSerializer(serializers.ModelSerializer):
    tier = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "full_name", "email", "phone", "avatar_url", "points_balance", "tier", "is_active"]

    def get_tier(self, user):
        return tier_for(user.lifetime_points)


class CustomerViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, GenericViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = CustomerSerializer
    queryset = User.objects.filter(is_staff=False)
    pagination_class = type("CustomerPagination", (PageNumberPagination,), {"page_size": 5})

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response.data["active_clients"] = User.objects.filter(is_staff=False, is_active=True).count()
        return response

    def retrieve(self, request, pk=None):
        customer = get_object_or_404(self.queryset, pk=pk)
        spend = customer.orders.exclude(status=Order.Status.CANCELLED).aggregate(spend=Sum("total"), average=Avg("total"))
        orders = customer.orders.prefetch_related(Prefetch("items", queryset=OrderItem.objects.only("order_id", "image_url")))[:10]
        history = LoyaltyTransaction.objects.filter(customer=customer).select_related("branch", "reward")[:20]
        next_tier, progress = tier_progress(customer.lifetime_points)

        return Response({
            **CustomerSerializer(customer).data,
            "shipping_address": customer.shipping_address,
            "next_tier": next_tier,
            "tier_progress": progress,
            "lifetime_spend": money(spend["spend"]),
            "avg_order_value": money(spend["average"]),
            "orders": [
                {"id": o.id, "number": o.number, "created_at": o.created_at, "status": o.status, "total": str(o.total),
                 "images": [i.image_url for i in o.items.all()]}
                for o in orders
            ],
            "loyalty_history": [
                {"id": t.id, "kind": t.kind, "channel": t.channel, "branch_name": t.branch.name if t.branch else None,
                 "reward_name": t.reward.name if t.reward else None, "created_at": t.created_at, "reference": t.reference,
                 "purchase_amount": str(t.purchase_amount), "points": t.points, "balance_after": t.balance_after}
                for t in history
            ],
        })

    @action(detail=False)
    def lookup(self, request):
        """Finds an active customer by exact email (Register Purchase step 1)."""
        email = request.query_params.get("email", "").strip()
        customer = get_object_or_404(User, ~Q(email=""), email__iexact=email, is_staff=False)
        return Response(CustomerSerializer(customer).data)
