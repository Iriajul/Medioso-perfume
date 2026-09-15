from rest_framework import serializers
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from Apps.common.media import delete_image, upload_image, validate_image
from Apps.common.stats import count_trend
from Apps.loyalty.models import LoyaltyTransaction, Reward


class RewardSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(write_only=True, required=False, validators=[validate_image])

    class Meta:
        model = Reward
        fields = ["id", "name", "points_required", "category", "eligibility", "description", "image", "image_url", "is_active"]
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
