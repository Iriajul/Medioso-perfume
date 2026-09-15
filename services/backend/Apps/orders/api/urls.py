from rest_framework.routers import SimpleRouter

from Apps.orders.api.views import OrderViewSet

app_name = "orders"

router = SimpleRouter()
router.register("admin/orders", OrderViewSet, basename="order")

urlpatterns = router.urls
