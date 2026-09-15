from django.urls import path
from rest_framework.routers import SimpleRouter

from Apps.catalog.api import app
from Apps.catalog.api.views import BannerViewSet, CategoryViewSet, ProductViewSet

app_name = "catalog"

router = SimpleRouter()
router.register("admin/categories", CategoryViewSet, basename="category")
router.register("admin/products", ProductViewSet, basename="product")
router.register("admin/banners", BannerViewSet, basename="banner")
router.register("app/products", app.ProductViewSet, basename="app-product")
router.register("app/saved-products", app.SavedProductViewSet, basename="app-saved-product")

urlpatterns = [
    path("app/categories/", app.CategoryListView.as_view(), name="app-categories"),
    path("app/banners/", app.BannerListView.as_view(), name="app-banners"),
    path("app/products/<int:product_id>/reviews/", app.ProductReviewsView.as_view(), name="app-product-reviews"),
    *router.urls,
]
