from django.db.models import Count, Sum
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from Apps.branches.models import Branch
from Apps.catalog.models import Banner, Category, Product
from Apps.common.media import delete_image, upload_image, validate_image
from Apps.common.stats import money
from Apps.orders.models import Order

IMAGE_SLOTS = ["image_1", "image_2", "image_3"]


def page_size(n):
    return type("Pagination", (PageNumberPagination,), {"page_size": n})


class AdminModelViewSet(ModelViewSet):
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser, JSONParser]


# ─── Categories ────────────────────────────────────────────────────────


class CategorySerializer(serializers.ModelSerializer):
    image = serializers.ImageField(write_only=True, required=False, validators=[validate_image])
    products_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Category
        fields = ["id", "name", "type", "description", "image", "image_url", "products_count", "created_at"]
        read_only_fields = ["image_url", "created_at"]

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


class CategoryViewSet(AdminModelViewSet):
    queryset = Category.objects.annotate(products_count=Count("products")).order_by("name")
    serializer_class = CategorySerializer
    pagination_class = page_size(5)

    @action(detail=False, pagination_class=None)
    def options(self, request):
        """All categories as {id, name} for select inputs."""
        return Response(list(Category.objects.values("id", "name")))

    def perform_destroy(self, instance):
        if instance.products_count:
            raise serializers.ValidationError({"detail": "This category still has products. Move or delete them first."})
        public_id = instance.image_public_id
        instance.delete()
        delete_image(public_id)


# ─── Products ──────────────────────────────────────────────────────────


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    sku = serializers.CharField(read_only=True)
    branches = serializers.PrimaryKeyRelatedField(many=True, queryset=Branch.objects.all(), required=False)
    image_urls = serializers.SerializerMethodField()
    image_1 = serializers.ImageField(write_only=True, required=False, validators=[validate_image])
    image_2 = serializers.ImageField(write_only=True, required=False, validators=[validate_image])
    image_3 = serializers.ImageField(write_only=True, required=False, validators=[validate_image])

    class Meta:
        model = Product
        fields = [
            "id", "sku", "name", "category", "category_name", "price", "stock", "description",
            "is_featured", "branches", "image_urls", *IMAGE_SLOTS, "created_at",
        ]
        read_only_fields = ["created_at"]

    def get_image_urls(self, obj):
        """Three slots, each a URL or null."""
        return [(img or {}).get("url") for img in (obj.images + [None] * 3)[:3]]

    def validate(self, attrs):
        has_image = any(attrs.get(slot) for slot in IMAGE_SLOTS) or (self.instance and any(self.instance.images))
        if not has_image:
            raise serializers.ValidationError({"image_1": "Upload at least one product image."})
        return attrs

    def _apply_images(self, validated_data, current):
        """Uploads new slot files; returns (images, public_ids_to_delete)."""
        images, replaced = (current + [None] * 3)[:3], []
        for i, slot in enumerate(IMAGE_SLOTS):
            if file := validated_data.pop(slot, None):
                if images[i]:
                    replaced.append(images[i]["public_id"])
                url, public_id = upload_image(file, "products")
                images[i] = {"url": url, "public_id": public_id}
        return images, replaced

    def create(self, validated_data):
        validated_data["images"], _ = self._apply_images(validated_data, [])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data["images"], replaced = self._apply_images(validated_data, instance.images)
        instance = super().update(instance, validated_data)
        for public_id in replaced:
            delete_image(public_id)
        return instance


class ProductViewSet(AdminModelViewSet):
    queryset = Product.objects.select_related("category").prefetch_related("branches")
    serializer_class = ProductSerializer
    pagination_class = page_size(4)

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response.data["in_stock"] = Product.objects.aggregate(total=Sum("stock"))["total"] or 0
        revenue = Order.objects.exclude(status=Order.Status.CANCELLED).aggregate(total=Sum("total"))["total"]
        response.data["revenue"] = money(revenue)
        return response

    def perform_destroy(self, instance):
        public_ids = [img["public_id"] for img in instance.images if img]
        instance.delete()
        for public_id in public_ids:
            delete_image(public_id)


# ─── Banners ───────────────────────────────────────────────────────────


class BannerSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(write_only=True, required=False, validators=[validate_image])
    status = serializers.CharField(read_only=True)

    class Meta:
        model = Banner
        fields = ["id", "title", "image", "image_url", "starts_on", "ends_on", "is_active", "status"]
        read_only_fields = ["image_url"]

    def validate(self, attrs):
        if self.instance is None and "image" not in attrs:
            raise serializers.ValidationError({"image": "A banner image is required."})
        starts = attrs.get("starts_on", getattr(self.instance, "starts_on", None))
        ends = attrs.get("ends_on", getattr(self.instance, "ends_on", None))
        if starts and ends and ends < starts:
            raise serializers.ValidationError({"ends_on": "End date must be on or after the start date."})
        return attrs

    def create(self, validated_data):
        validated_data["image_url"], validated_data["image_public_id"] = upload_image(validated_data.pop("image"), "banners")
        return super().create(validated_data)

    def update(self, instance, validated_data):
        old_public_id = None
        if image := validated_data.pop("image", None):
            old_public_id = instance.image_public_id
            validated_data["image_url"], validated_data["image_public_id"] = upload_image(image, "banners")
        instance = super().update(instance, validated_data)
        delete_image(old_public_id)
        return instance


class BannerViewSet(AdminModelViewSet):
    queryset = Banner.objects.all()
    serializer_class = BannerSerializer
    pagination_class = None

    def perform_destroy(self, instance):
        public_id = instance.image_public_id
        instance.delete()
        delete_image(public_id)
