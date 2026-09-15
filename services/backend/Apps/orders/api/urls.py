from django.urls import path
from rest_framework.routers import SimpleRouter

from Apps.orders.api import app
from Apps.orders.api.views import OrderViewSet

app_name = "orders"

router = SimpleRouter()
router.register("admin/orders", OrderViewSet, basename="order")
router.register("app/cart", app.CartViewSet, basename="app-cart")
router.register("app/orders", app.OrderViewSet, basename="app-order")

urlpatterns = [
    path("app/payments/stripe/webhook/", app.StripeWebhookView.as_view(), name="stripe-webhook"),
    *router.urls,
]
