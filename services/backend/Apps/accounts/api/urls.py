from django.urls import path

from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import TokenBlacklistView, TokenRefreshView

from Apps.accounts.api.customers import CustomerViewSet
from Apps.accounts.api.staff import StaffViewSet
from Apps.accounts.api.views import (
    AdminLoginView,
    ChangePasswordView,
    MeView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
)

app_name = "accounts"

urlpatterns = [
    path("auth/login/", AdminLoginView.as_view(), name="admin-login"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("auth/logout/", TokenBlacklistView.as_view(), name="logout"),
    path("auth/me/", MeView.as_view(), name="me"),
    path("auth/change-password/", ChangePasswordView.as_view(), name="change-password"),
    path("auth/password-reset/", PasswordResetRequestView.as_view(), name="password-reset"),
    path("auth/password-reset/confirm/", PasswordResetConfirmView.as_view(), name="password-reset-confirm"),
]

router = SimpleRouter()
router.register("admin/customers", CustomerViewSet, basename="customer")
router.register("admin/staff", StaffViewSet, basename="staff")
urlpatterns += router.urls
