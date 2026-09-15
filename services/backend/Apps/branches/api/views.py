from django.utils import timezone
from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAdminUser
from rest_framework.viewsets import ModelViewSet

from Apps.branches.models import Branch
from Apps.common.media import delete_image, upload_image, validate_image


class BranchSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(write_only=True, required=False, validators=[validate_image])

    class Meta:
        model = Branch
        fields = [
            "id", "name", "address", "phone",
            "weekday_opens", "weekday_closes", "sunday_opens", "sunday_closes",
            "latitude", "longitude", "image", "image_url", "created_at",
        ]
        read_only_fields = ["image_url", "created_at"]

    def validate(self, attrs):
        for opens, closes in [("weekday_opens", "weekday_closes"), ("sunday_opens", "sunday_closes")]:
            o, c = attrs.get(opens, getattr(self.instance, opens, None)), attrs.get(closes, getattr(self.instance, closes, None))
            if o and c and o >= c:
                raise serializers.ValidationError({closes: "Closing time must be after opening time."})
        return attrs

    def create(self, validated_data):
        if image := validated_data.pop("image", None):
            validated_data["image_url"], validated_data["image_public_id"] = upload_image(image, "branches")
        return super().create(validated_data)

    def update(self, instance, validated_data):
        old_public_id = None
        if image := validated_data.pop("image", None):
            old_public_id = instance.image_public_id
            validated_data["image_url"], validated_data["image_public_id"] = upload_image(image, "branches")
        instance = super().update(instance, validated_data)
        delete_image(old_public_id)
        return instance


class BranchPagination(PageNumberPagination):
    page_size = 5


class BranchViewSet(ModelViewSet):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    permission_classes = [IsAdminUser]
    pagination_class = BranchPagination
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        today = timezone.localdate()
        quarter_start = today.replace(month=3 * ((today.month - 1) // 3) + 1, day=1)
        response.data["added_this_quarter"] = Branch.objects.filter(created_at__date__gte=quarter_start).count()
        return response

    def perform_destroy(self, instance):
        public_id = instance.image_public_id
        instance.delete()
        delete_image(public_id)
