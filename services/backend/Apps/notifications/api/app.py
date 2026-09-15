"""Customer app: notification inbox."""

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from Apps.notifications.models import UserNotification


class UserNotificationSerializer(serializers.ModelSerializer):
    order_number = serializers.SerializerMethodField()

    class Meta:
        model = UserNotification
        fields = ["id", "category", "title", "body", "order", "order_number", "is_read", "created_at"]
        read_only_fields = ["category", "title", "body", "order", "created_at"]

    def get_order_number(self, notification):
        return f"MAD-{notification.order_id:05d}" if notification.order_id else None


class UserNotificationViewSet(mixins.ListModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    """Inbox filtered by `?category=offers|rewards|orders`. PATCH `{is_read}` on one, POST `read-all/`."""

    serializer_class = UserNotificationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["category", "is_read"]
    http_method_names = ["get", "patch", "post"]

    def get_queryset(self):
        return UserNotification.objects.filter(user=self.request.user)

    @action(detail=False, methods=["get"], url_path="unread-count")
    def unread_count(self, request):
        return Response({"unread": self.get_queryset().filter(is_read=False).count()})

    @action(detail=False, methods=["post"], url_path="read-all")
    def read_all(self, request):
        self.get_queryset().filter(is_read=False).update(is_read=True)
        return Response(status=status.HTTP_204_NO_CONTENT)
