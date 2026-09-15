from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

from Apps.orders.models import Order


def send_invoice(order_id):
    """Emails the customer their invoice once the order is confirmed (card paid, or cash on delivery placed)."""
    order = Order.objects.select_related("customer").prefetch_related("items").get(pk=order_id)
    context = {"order": order, "items": order.items.all(), "logo_url": f"{settings.ADMIN_URL}/logo.png"}
    # A mail outage must not fail checkout or make Stripe retry the webhook.
    send_mail(
        f"Your Mad Perfume invoice {order.number}",
        f"Thank you for your order {order.number}. Total: ${order.total}.",
        None,
        [order.customer.email],
        html_message=render_to_string("orders/emails/invoice.html", context),
        fail_silently=True,
    )
