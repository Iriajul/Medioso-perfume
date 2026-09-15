"""Loyalty rules: tiers, earning and redeeming. All balance changes go through here."""

from decimal import ROUND_FLOOR, Decimal

from django.conf import settings
from django.db import IntegrityError, transaction
from rest_framework.exceptions import ValidationError

from Apps.accounts.models import User
from Apps.loyalty.models import LoyaltyTransaction

# Tier by lifetime points earned (lower bound).
TIERS = [("silver", 0), ("gold", 2_500), ("platinum", 7_500), ("diamond", 15_000)]


def tier_for(lifetime_points):
    return next(name for name, floor in reversed(TIERS) if lifetime_points >= floor)


def tier_progress(lifetime_points):
    """(next_tier, percent towards it) or (None, 100) at the top tier."""
    for (name, floor), (next_name, next_floor) in zip(TIERS, TIERS[1:]):
        if lifetime_points < next_floor:
            return next_name, int((lifetime_points - floor) * 100 / (next_floor - floor))
    return None, 100


def points_for_amount(amount):
    return int((Decimal(amount) * Decimal(settings.POINTS_PER_DOLLAR)).to_integral_value(ROUND_FLOOR))


def _apply(customer_id, **fields):
    with transaction.atomic():
        customer = User.objects.select_for_update().get(pk=customer_id)
        customer.points_balance += fields["points"]
        if fields["points"] < 0 and customer.points_balance < 0:
            raise ValidationError({"points": "Not enough points."})
        if fields["points"] > 0:
            customer.lifetime_points += fields["points"]
        customer.save(update_fields=["points_balance", "lifetime_points", "updated_at"])
        return LoyaltyTransaction.objects.create(customer=customer, balance_after=customer.points_balance, **fields)


def earn_for_order(order, created_by=None):
    """Awards points for an order once (app orders on delivery, in-store immediately)."""
    points = points_for_amount(order.total)
    if points <= 0:
        return None
    try:
        return _apply(
            order.customer_id, kind="earned", channel=order.channel, branch_id=order.branch_id, order=order,
            purchase_amount=order.total, points=points, created_by=created_by, note=order.notes,
        )
    except IntegrityError:  # already awarded
        return None


def redeem(customer, reward, channel, branch=None, created_by=None):
    return _apply(
        customer.pk, kind="redeemed", channel=channel, branch=branch, reward=reward,
        points=-reward.points_required, created_by=created_by,
    )
