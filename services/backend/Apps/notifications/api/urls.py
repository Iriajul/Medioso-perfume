from rest_framework.routers import SimpleRouter

from Apps.notifications.api.views import NotificationViewSet

app_name = "notifications"

router = SimpleRouter()
router.register("admin/notifications", NotificationViewSet, basename="notification")

urlpatterns = router.urls
