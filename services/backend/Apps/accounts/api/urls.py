from django.urls import path

from rest_framework_simplejwt.views import TokenBlacklistView, TokenRefreshView

from Apps.accounts.api.views import AdminLoginView, PasswordResetConfirmView, PasswordResetRequestView

app_name = "accounts"

urlpatterns = [
    path("auth/login/", AdminLoginView.as_view(), name="admin-login"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("auth/logout/", TokenBlacklistView.as_view(), name="logout"),
    path("auth/password-reset/", PasswordResetRequestView.as_view(), name="password-reset"),
    path("auth/password-reset/confirm/", PasswordResetConfirmView.as_view(), name="password-reset-confirm"),
]
