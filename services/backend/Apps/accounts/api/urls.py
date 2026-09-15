from django.urls import path

from Apps.accounts.api.views import AdminLoginView

app_name = "accounts"

urlpatterns = [
    path("auth/login/", AdminLoginView.as_view(), name="admin-login"),
]
