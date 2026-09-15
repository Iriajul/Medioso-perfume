"""Customer app: catalog browsing, reviews and saved items."""

import django_filters
from django.db import IntegrityError, transaction
from django.db.models import Avg, Count, Exists, IntegerField, OuterRef, Q, Subquery, Sum, Value
from django.db.models.functions import Coalesce
from django.utils import timezone
from rest_framework import filters, generics, mixins, serializers, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated

from Apps.catalog.models import Banner, Category, Product, Review, SavedProduct
from Apps.loyalty import services as loyalty
from Apps.orders.models import Order, OrderItem


class AppCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "type", "description", "image_url"]


class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.order_by("name")
    serializer_class = AppCategorySerializer
    permission_classes = [AllowAny]
    pagination_class = None


class AppBannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = ["id", "title", "image_url", "starts_on", "ends_on"]


class BannerListView(generics.ListAPIView):
    """Banners live today (home carousel)."""

    serializer_class = AppBannerSerializer
    permission_classes = [AllowAny]
    pagination_class = None

    def get_queryset(self):
        today = timezone.localdate()
        return Banner.objects.filter(is_active=True, starts_on__lte=today, ends_on__gte=today)


# ─── Products ──────────────────────────────────────────────────────────


class ProductFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    brand = django_filters.CharFilter(lookup_expr="iexact")

    class Meta:
        model = Product
        fields = ["category", "concentration", "is_featured", "brand", "min_price", "max_price"]


class ProductListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name")
    image_url = serializers.SerializerMethodField()
    notes = serializers.ListField(source="notes_list")
    rating = serializers.FloatField()
    reviews_count = serializers.IntegerField()
    is_saved = serializers.BooleanField()
    in_stock = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ["id", "name", "brand", "category", "category_name", "concentration", "size", "notes", "price",
                  "image_url", "rating", "reviews_count", "is_saved", "in_stock"]

    def get_image_url(self, product):
        return next((img["url"] for img in product.images if img), None)

    def get_in_stock(self, product):
        return product.stock > 0


class ProductDetailSerializer(ProductListSerializer):
    image_urls = serializers.SerializerMethodField()
    branches = serializers.SerializerMethodField()

    class Meta(ProductListSerializer.Meta):
        fields = [*ProductListSerializer.Meta.fields, "description", "image_urls", "branches"]

    def get_image_urls(self, product):
        return [img["url"] for img in product.images if img]

    def get_branches(self, product):
        return [{"id": b.id, "name": b.name, "city": b.city} for b in product.branches.all()]


def with_app_fields(queryset, user):
    """Rating, review count, units sold and saved flag as subqueries (no joins, no N+1)."""
    reviews = Review.objects.filter(product=OuterRef("pk")).values("product")
    sold = (OrderItem.objects.filter(product=OuterRef("pk")).exclude(order__status=Order.Status.CANCELLED)
            .values("product").annotate(total=Sum("quantity")).values("total"))
    saved = SavedProduct.objects.filter(product=OuterRef("pk"), user=user) if user.is_authenticated else None
    return queryset.select_related("category").annotate(
        rating=Coalesce(Subquery(reviews.annotate(avg=Avg("rating")).values("avg")), Value(0.0)),
        reviews_count=Coalesce(Subquery(reviews.annotate(n=Count("pk")).values("n"), output_field=IntegerField()), 0),
        sold=Coalesce(Subquery(sold, output_field=IntegerField()), 0),
        is_saved=Exists(saved) if saved is not None else Value(False),
    )


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """Search `?search=`, filter (category, concentration, brand, min/max_price, is_featured),
    sort `?ordering=` price, -price, -created_at (new arrivals), -sold (best sellers), -rating."""

    permission_classes = [AllowAny]
    filterset_class = ProductFilter
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "brand", "notes", "description", "category__name"]
    ordering_fields = ["price", "created_at", "sold", "rating"]
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = with_app_fields(Product.objects.all(), self.request.user)
        if self.action == "retrieve":
            queryset = queryset.prefetch_related("branches")
        return queryset

    def get_serializer_class(self):
        return ProductDetailSerializer if self.action == "retrieve" else ProductListSerializer


# ─── Reviews ───────────────────────────────────────────────────────────


class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.full_name", read_only=True)

    class Meta:
        model = Review
        fields = ["id", "user_name", "rating", "comment", "created_at"]


class ProductReviewsView(generics.ListCreateAPIView):
    """GET a product's reviews; POST one review per delivered purchase (earns loyalty points)."""

    serializer_class = ReviewSerializer

    def get_permissions(self):
        return [IsAuthenticated()] if self.request.method == "POST" else [AllowAny()]

    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs["product_id"]).select_related("user")

    def perform_create(self, serializer):
        product = generics.get_object_or_404(Product, pk=self.kwargs["product_id"])
        purchased = OrderItem.objects.filter(
            product=product, order__customer=self.request.user, order__status=Order.Status.DELIVERED
        ).exists()
        if not purchased:
            raise serializers.ValidationError({"detail": "You can review products from your delivered orders."})
        try:
            with transaction.atomic():
                review = serializer.save(product=product, user=self.request.user)
                loyalty.earn_for_review(review)
        except IntegrityError:
            raise serializers.ValidationError({"detail": "You have already reviewed this product."})


# ─── Saved items ───────────────────────────────────────────────────────


class SavedProductSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())

    class Meta:
        model = SavedProduct
        fields = ["product"]


class SavedProductViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    """GET saved products, POST {product} to save, DELETE /<product_id>/ to unsave."""

    permission_classes = [IsAuthenticated]
    lookup_field = "product_id"

    def get_queryset(self):
        if self.action == "list":
            return with_app_fields(Product.objects.filter(Exists(
                SavedProduct.objects.filter(product=OuterRef("pk"), user=self.request.user))), self.request.user)
        return SavedProduct.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        return ProductListSerializer if self.action == "list" else SavedProductSerializer

    def perform_create(self, serializer):
        SavedProduct.objects.get_or_create(user=self.request.user, product=serializer.validated_data["product"])
