from django.urls import path

from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import TokenBlacklistView, TokenRefreshView

from Apps.accounts.api import app
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
    # Customer app
    path("app/auth/register/", app.RegisterView.as_view(), name="app-register"),
    path("app/auth/login/", app.LoginView.as_view(), name="app-login"),
    path("app/auth/password-reset/code/", app.ResetCodeRequestView.as_view(), name="app-reset-code"),
    path("app/auth/password-reset/verify/", app.ResetCodeVerifyView.as_view(), name="app-reset-verify"),
    path("app/me/", app.MeView.as_view(), name="app-me"),
    path("app/me/change-password/", app.AppChangePasswordView.as_view(), name="app-change-password"),
    path("app/devices/", app.DeviceTokenView.as_view(), name="app-devices"),
    path("app/devices/<str:token>/", app.DeviceTokenView.as_view(), name="app-device"),
]

router = SimpleRouter()
router.register("admin/customers", CustomerViewSet, basename="customer")
router.register("admin/staff", StaffViewSet, basename="staff")
urlpatterns += router.urls
