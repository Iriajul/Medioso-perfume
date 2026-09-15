from rest_framework.routers import SimpleRouter

from Apps.branches.api.views import BranchViewSet

app_name = "branches"

router = SimpleRouter()
router.register("admin/branches", BranchViewSet, basename="branch")

urlpatterns = router.urls
