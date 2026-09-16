from django.urls import path
from rest_framework.routers import SimpleRouter

from Apps.loyalty.api import app
from Apps.loyalty.api.views import RedemptionViewSet, RewardViewSet

app_name = "loyalty"

router = SimpleRouter()
router.register("admin/rewards", RewardViewSet, basename="reward")
router.register("admin/redemptions", RedemptionViewSet, basename="redemption")
router.register("app/rewards", app.RewardViewSet, basename="app-reward")

urlpatterns = [
    path("app/loyalty/", app.LoyaltySummaryView.as_view(), name="app-loyalty"),
    path("app/loyalty/transactions/", app.TransactionListView.as_view(), name="app-loyalty-transactions"),
    path("app/redemptions/", app.RedemptionListView.as_view(), name="app-redemptions"),
    *router.urls,
]
