from rest_framework.routers import SimpleRouter

from Apps.catalog.api.views import CategoryViewSet

app_name = "catalog"

router = SimpleRouter()
router.register("admin/categories", CategoryViewSet, basename="category")

urlpatterns = router.urls
