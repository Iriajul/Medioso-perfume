from rest_framework.routers import SimpleRouter

from Apps.notifications.api import app
from Apps.notifications.api.views import NotificationViewSet

app_name = "notifications"

router = SimpleRouter()
router.register("admin/notifications", NotificationViewSet, basename="notification")
router.register("app/notifications", app.UserNotificationViewSet, basename="app-notification")

urlpatterns = router.urls
