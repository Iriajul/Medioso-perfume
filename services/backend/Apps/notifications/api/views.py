from django.db import transaction
from rest_framework import mixins, serializers
from rest_framework.permissions import IsAdminUser
from rest_framework.viewsets import GenericViewSet

from Apps.accounts.models import User
from Apps.loyalty.services import TIERS
from Apps.notifications.models import Notification, UserNotification, push_after_commit


def audience_queryset(audience):
    customers = User.objects.filter(is_staff=False, is_active=True)
    if audience == Notification.Audience.ALL:
        return customers
    floors = dict(TIERS)
    names = [name for name, _ in TIERS]
    next_floor = floors[names[names.index(audience) + 1]] if audience != names[-1] else None
    customers = customers.filter(lifetime_points__gte=floors[audience])
    return customers.filter(lifetime_points__lt=next_floor) if next_floor is not None else customers


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ["id", "title", "body", "audience", "recipients_count", "status", "created_at"]
        read_only_fields = ["recipients_count", "status", "created_at"]

    @transaction.atomic
    def create(self, validated_data):
        recipients = list(audience_queryset(validated_data["audience"]).values_list("pk", flat=True))
        broadcast = super().create({
            **validated_data, "recipients_count": len(recipients), "status": Notification.Status.SENT,
            "created_by": self.context["request"].user,
        })
        rows = UserNotification.objects.bulk_create(
            (UserNotification(user_id=pk, broadcast=broadcast, category=UserNotification.Category.OFFERS,
                              title=broadcast.title, body=broadcast.body) for pk in recipients),
            batch_size=1000,
        )
        push_after_commit(rows)
        return broadcast


class NotificationViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, GenericViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAdminUser]
