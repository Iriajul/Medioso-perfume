from rest_framework.routers import SimpleRouter

from Apps.catalog.api.views import BannerViewSet, CategoryViewSet, ProductViewSet

app_name = "catalog"

router = SimpleRouter()
router.register("admin/categories", CategoryViewSet, basename="category")
router.register("admin/products", ProductViewSet, basename="product")
router.register("admin/banners", BannerViewSet, basename="banner")

urlpatterns = router.urls
