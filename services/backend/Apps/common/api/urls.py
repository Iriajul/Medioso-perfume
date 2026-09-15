from django.urls import path

from Apps.common.api.views import HealthCheckView

app_name = "common"

urlpatterns = [
    path("health/", HealthCheckView.as_view(), name="health"),
]
