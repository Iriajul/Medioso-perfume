from django.urls import path

from Apps.dashboard.api.views import DashboardView

app_name = "dashboard"

urlpatterns = [
    path("admin/dashboard/", DashboardView.as_view(), name="overview"),
]
