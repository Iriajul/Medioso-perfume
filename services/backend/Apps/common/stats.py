from datetime import timedelta

from django.db.models import Count, Q
from django.utils import timezone


def trend_percent(current, previous):
    """Change vs the previous period, or None without a baseline."""
    return round((current - previous) / previous * 100) if previous else None


def last_30_days_filters(field="created_at"):
    """Q filters for (last 30 days, the 30 days before) on a datetime field."""
    now = timezone.now()
    return (
        Q(**{f"{field}__gte": now - timedelta(days=30)}),
        Q(**{f"{field}__gte": now - timedelta(days=60), f"{field}__lt": now - timedelta(days=30)}),
    )


def count_trend(queryset, field="created_at"):
    """(total, trend %) in one query."""
    current, previous = last_30_days_filters(field)
    counts = queryset.aggregate(total=Count("id"), current=Count("id", filter=current), previous=Count("id", filter=previous))
    return counts["total"], trend_percent(counts["current"], counts["previous"])


def money(value):
    """Decimal/None -> "0.00" string with exactly two decimals."""
    return f"{(value or 0):.2f}"
