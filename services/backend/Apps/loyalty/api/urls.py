from rest_framework.routers import SimpleRouter

from Apps.loyalty.api.views import RewardViewSet

app_name = "loyalty"

router = SimpleRouter()
router.register("admin/rewards", RewardViewSet, basename="reward")

urlpatterns = router.urls
