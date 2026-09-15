"""Root URL configuration for the Mad Perfume backend.

API routes are versioned under /api/v1/. Each app contributes its own
`api/urls.py`, included here as features land.
"""

from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

api_v1_patterns = [
    path("", include("Apps.common.api.urls")),
    path("", include("Apps.accounts.api.urls")),
    path("", include("Apps.dashboard.api.urls")),
    path("", include("Apps.catalog.api.urls")),
    path("", include("Apps.branches.api.urls")),
]

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include((api_v1_patterns, "v1"))),
    # OpenAPI schema + interactive docs (shared with the mobile developer)
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("", RedirectView.as_view(pattern_name="swagger-ui"), name="root-redirect"),
]
