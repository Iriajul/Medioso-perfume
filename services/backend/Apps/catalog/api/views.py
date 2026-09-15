from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAdminUser
from rest_framework.viewsets import ModelViewSet

from Apps.catalog.models import Category
from Apps.common.media import delete_image, upload_image, validate_image


class CategorySerializer(serializers.ModelSerializer):
    image = serializers.ImageField(write_only=True, required=False, validators=[validate_image])
    # Filled in with a Count annotation once products exist.
    products_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["id", "name", "type", "description", "image", "image_url", "products_count", "created_at"]
        read_only_fields = ["image_url", "created_at"]

    def get_products_count(self, obj):
        return getattr(obj, "products_count", 0)

    def validate(self, attrs):
        if self.instance is None and "image" not in attrs:
            raise serializers.ValidationError({"image": "A category image is required."})
        return attrs

    def create(self, validated_data):
        validated_data["image_url"], validated_data["image_public_id"] = upload_image(validated_data.pop("image"), "categories")
        return super().create(validated_data)

    def update(self, instance, validated_data):
        old_public_id = None
        if image := validated_data.pop("image", None):
            old_public_id = instance.image_public_id
            validated_data["image_url"], validated_data["image_public_id"] = upload_image(image, "categories")
        instance = super().update(instance, validated_data)
        delete_image(old_public_id)
        return instance


class CategoryPagination(PageNumberPagination):
    page_size = 5


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUser]
    pagination_class = CategoryPagination
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def perform_destroy(self, instance):
        public_id = instance.image_public_id
        instance.delete()
        delete_image(public_id)
