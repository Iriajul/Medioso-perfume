"""Customer app: points summary, history, rewards shop and redemptions."""

from django.conf import settings
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from Apps.loyalty import services as loyalty
from Apps.loyalty.models import LoyaltyTransaction, Reward
from Apps.notifications.models import UserNotification


class TransactionSerializer(serializers.ModelSerializer):
    reference = serializers.CharField(read_only=True)
    title = serializers.SerializerMethodField()
    branch_name = serializers.CharField(source="branch.name", default=None)

    class Meta:
        model = LoyaltyTransaction
        fields = ["id", "reference", "title", "kind", "reason", "channel", "branch_name", "purchase_amount", "points", "balance_after", "created_at"]

    def get_title(self, entry):
        if entry.reason == LoyaltyTransaction.Reason.REVIEW:
            return f"Product Review: {entry.review.product.name}" if entry.review else "Product Review"
        if entry.reason == LoyaltyTransaction.Reason.REWARD:
            return f"Reward: {entry.reward.name}" if entry.reward else "Reward"
        return f"Purchase: {entry.branch.name}" if entry.branch else "Purchase: Mobile App"


def transactions_for(user):
    return user.loyalty_transactions.select_related("branch", "reward", "review__product")


class TransactionListView(generics.ListAPIView):
    """Points history. Filter `?channel=app|branch`, `?kind=earned|redeemed`."""

    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["channel", "kind"]

    def get_queryset(self):
        return transactions_for(self.request.user)


class LoyaltySummaryView(generics.GenericAPIView):
    """Balance card, tier progress, earn rates and the latest activity."""

    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        next_tier, progress = loyalty.tier_progress(user.lifetime_points)
        floors = dict(loyalty.TIERS)
        return Response({
            "points_balance": user.points_balance,
            "lifetime_points": user.lifetime_points,
            "tier": loyalty.tier_for(user.lifetime_points),
            "next_tier": next_tier,
            "points_to_next_tier": floors[next_tier] - user.lifetime_points if next_tier else 0,
            "tier_progress": progress,
            "tiers": floors,
            "earn_rates": {"app": settings.POINTS_PER_DOLLAR_APP, "branch": settings.POINTS_PER_DOLLAR_BRANCH, "review": settings.REVIEW_POINTS},
            "recent_activity": self.get_serializer(transactions_for(user)[:5], many=True).data,
        })


class AppRewardSerializer(serializers.ModelSerializer):
    can_redeem = serializers.SerializerMethodField()

    class Meta:
        model = Reward
        fields = ["id", "name", "points_required", "category", "eligibility", "description", "image_url", "can_redeem"]

    def get_can_redeem(self, reward):
        return loyalty.can_redeem(self.context["request"].user, reward)


class RedemptionSerializer(serializers.ModelSerializer):
    voucher_code = serializers.CharField(source="reference")
    name = serializers.CharField(source="reward.name", default=None)
    image_url = serializers.CharField(source="reward.image_url", default=None)
    points = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = LoyaltyTransaction
        fields = ["id", "voucher_code", "reward", "name", "image_url", "points", "status", "created_at", "fulfilled_at"]

    def get_points(self, entry):
        return -entry.points

    def get_status(self, entry):
        return "delivered" if entry.fulfilled_at else "processing"


class RewardViewSet(viewsets.ReadOnlyModelViewSet):
    """Rewards shop; `can_redeem` checks balance and tier. POST `/<id>/redeem/` spends the points."""

    serializer_class = AppRewardSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None
    filterset_fields = ["category"]
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self):
        return Reward.objects.filter(is_active=True).order_by("points_required")

    @action(detail=True, methods=["post"], serializer_class=RedemptionSerializer)
    def redeem(self, request, pk=None):
        reward = self.get_object()
        if not loyalty.can_redeem(request.user, reward):
            raise serializers.ValidationError({"detail": "This reward isn't available for your points or tier yet."})
        entry = loyalty.redeem(request.user, reward, channel="app")
        UserNotification.objects.create(
            user=request.user, category=UserNotification.Category.REWARDS, title=f"{reward.name} redeemed",
            body=f"Present voucher {entry.reference} at any MAD boutique to collect your reward.",
        )
        return Response(RedemptionSerializer(entry).data, status=status.HTTP_201_CREATED)


class RedemptionListView(generics.ListAPIView):
    serializer_class = RedemptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.loyalty_transactions.filter(kind=LoyaltyTransaction.Kind.REDEEMED).select_related("reward")
