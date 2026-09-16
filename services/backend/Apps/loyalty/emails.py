from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

from Apps.loyalty.models import LoyaltyTransaction


def send_voucher(entry_id):
    """Emails the customer their voucher code after a redemption."""
    entry = LoyaltyTransaction.objects.select_related("customer", "reward").get(pk=entry_id)
    discount = entry.reward.discount_amount if entry.reward else 0
    context = {"entry": entry, "reward": entry.reward, "code": entry.reference, "discount": discount,
               "is_voucher": discount > 0, "logo_url": f"{settings.ADMIN_URL}/logo.png"}
    body = (f"Your voucher {entry.reference} is worth ${discount} off your next purchase."
            if discount > 0 else f"Present voucher {entry.reference} at any MAD boutique to collect your reward.")
    # A mail outage must never fail the redemption itself.
    send_mail(
        f"Your Mad Perfume reward: {entry.reward.name if entry.reward else entry.reference}",
        body, None, [entry.customer.email],
        html_message=render_to_string("loyalty/emails/voucher.html", context), fail_silently=True,
    )
