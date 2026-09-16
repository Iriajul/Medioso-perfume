from django.utils import timezone
from rest_framework import mixins, serializers
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from Apps.branches.models import Branch
from Apps.common.media import delete_image, upload_image, validate_image
from Apps.common.stats import count_trend
from Apps.loyalty.models import LoyaltyTransaction, Reward
from Apps.notifications.models import UserNotification


class RewardSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(write_only=True, required=False, validators=[validate_image])

    class Meta:
        model = Reward
        fields = ["id", "name", "points_required", "discount_amount", "category", "eligibility", "description", "image", "image_url", "is_active"]
        read_only_fields = ["image_url"]

    def validate(self, attrs):
        if self.instance is None and "image" not in attrs:
            raise serializers.ValidationError({"image": "A reward image is required."})
        return attrs

    def create(self, validated_data):
        validated_data["image_url"], validated_data["image_public_id"] = upload_image(validated_data.pop("image"), "rewards")
        return super().create(validated_data)

    def update(self, instance, validated_data):
        old_public_id = None
        if image := validated_data.pop("image", None):
            old_public_id = instance.image_public_id
            validated_data["image_url"], validated_data["image_public_id"] = upload_image(image, "rewards")
        instance = super().update(instance, validated_data)
        delete_image(old_public_id)
        return instance


class RewardViewSet(ModelViewSet):
    queryset = Reward.objects.all()
    serializer_class = RewardSerializer
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    pagination_class = None

    def list(self, request, *args, **kwargs):
        total, trend = count_trend(LoyaltyTransaction.objects.filter(kind=LoyaltyTransaction.Kind.REDEEMED))
        return Response({
            "total_redemptions": total,
            "redemptions_trend": trend,
            "results": self.get_serializer(self.get_queryset(), many=True).data,
        })

    def perform_destroy(self, instance):
        public_id = instance.image_public_id
        instance.delete()
        delete_image(public_id)


class RedemptionSerializer(serializers.ModelSerializer):
    voucher_code = serializers.CharField(source="reference", read_only=True)
    customer_name = serializers.CharField(source="customer.full_name", read_only=True)
    customer_email = serializers.CharField(source="customer.email", read_only=True)
    reward_name = serializers.CharField(source="reward.name", default=None, read_only=True)
    reward_image = serializers.CharField(source="reward.image_url", default=None, read_only=True)
    branch_name = serializers.CharField(source="branch.name", default=None, read_only=True)
    collected_by = serializers.CharField(source="fulfilled_by.full_name", default=None, read_only=True)
    discount_amount = serializers.DecimalField(source="reward.discount_amount", max_digits=10, decimal_places=2, default=None, read_only=True)
    used_on_order = serializers.SerializerMethodField()
    points = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = LoyaltyTransaction
        fields = ["id", "voucher_code", "customer", "customer_name", "customer_email", "reward", "reward_name",
                  "reward_image", "points", "discount_amount", "channel", "branch_name", "status", "used_on_order",
                  "created_at", "fulfilled_at", "collected_by"]

    def get_points(self, entry):
        return -entry.points

    def get_status(self, entry):
        if not entry.fulfilled_at:
            return "processing"
        return "used" if entry.reward and entry.reward.discount_amount > 0 else "collected"

    def get_used_on_order(self, entry):
        return entry.order.number if entry.order_id else None


class RedemptionViewSet(mixins.ListModelMixin, GenericViewSet):
    """Vouchers customers redeemed with points. `?status=processing|collected`, `?search=` code, name or email."""

    permission_classes = [IsAdminUser]
    serializer_class = RedemptionSerializer
    filter_backends = [SearchFilter]
    search_fields = ["customer__full_name", "customer__email", "reward__name"]

    def get_queryset(self):
        queryset = LoyaltyTransaction.objects.filter(kind=LoyaltyTransaction.Kind.REDEEMED).select_related(
            "customer", "reward", "branch", "fulfilled_by", "order")
        status_filter = self.request.query_params.get("status")
        if status_filter == "processing":
            queryset = queryset.filter(fulfilled_at=None)
        elif status_filter == "collected":
            queryset = queryset.exclude(fulfilled_at=None)
        if code := self.request.query_params.get("code"):
            queryset = queryset.filter(pk=code.upper().removeprefix("RD-").lstrip("0") or 0)
        return queryset

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response.data["pending_count"] = self.get_queryset().filter(fulfilled_at=None).count()
        return response

    @action(detail=True, methods=["post"])
    def collect(self, request, pk=None):
        """Marks the voucher handed over at a boutique. Any staff member may do this.

        The boutique defaults to the staff member's own; head office can pass `{"branch": id}`."""
        entry = self.get_object()
        if entry.fulfilled_at:
            raise serializers.ValidationError({"detail": "This voucher was already collected."})
        if entry.reward and entry.reward.discount_amount > 0:
            raise serializers.ValidationError({"detail": "Discount vouchers are marked used automatically at checkout."})
        branch = request.data.get("branch")
        entry.fulfilled_at = timezone.now()
        entry.fulfilled_by = request.user
        entry.branch = Branch.objects.filter(pk=branch).first() if branch else (entry.branch or request.user.branch)
        entry.save(update_fields=["fulfilled_at", "fulfilled_by", "branch"])
        UserNotification.deliver(
            user_id=entry.customer_id, category=UserNotification.Category.REWARDS,
            title=f"{entry.reward.name if entry.reward else 'Reward'} collected",
            body=f"Voucher {entry.reference} was collected. Enjoy your reward.",
        )
        return Response(self.get_serializer(entry).data)
