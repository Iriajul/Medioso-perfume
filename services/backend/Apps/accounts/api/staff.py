from django.db import transaction
from django.db.models import Count, Q
from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAdminUser
from rest_framework.viewsets import ModelViewSet

from Apps.accounts.emails import send_password_link
from Apps.accounts.models import User
from Apps.common.media import delete_image, upload_image, validate_image


class StaffSerializer(serializers.ModelSerializer):
    photo = serializers.ImageField(write_only=True, required=False, validators=[validate_image])
    branch_name = serializers.CharField(source="branch.name", read_only=True, default=None)

    class Meta:
        model = User
        fields = ["id", "full_name", "email", "branch", "branch_name", "job_title", "is_active", "avatar_url", "photo"]
        read_only_fields = ["avatar_url"]
        extra_kwargs = {"branch": {"required": True, "allow_null": False}, "job_title": {"required": True, "allow_blank": False}}

    def _upload(self, validated_data):
        if photo := validated_data.pop("photo", None):
            validated_data["avatar_url"], validated_data["avatar_public_id"] = upload_image(photo, "staff")

    def create(self, validated_data):
        self._upload(validated_data)
        with transaction.atomic():
            # No usable password until the invite link is used.
            user = User.objects.create_user(password=None, is_staff=True, **validated_data)
            transaction.on_commit(lambda: send_password_link(user, kind="invite"))
        return user

    def update(self, instance, validated_data):
        old = instance.avatar_public_id if "photo" in validated_data else None
        self._upload(validated_data)
        instance = super().update(instance, validated_data)
        delete_image(old)
        return instance


class StaffViewSet(ModelViewSet):
    """Staff directory: non-superuser admin accounts assigned to branches."""

    queryset = User.objects.filter(is_staff=True, is_superuser=False).select_related("branch")
    serializer_class = StaffSerializer
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    pagination_class = type("StaffPagination", (PageNumberPagination,), {"page_size": 4})

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        stats = User.objects.filter(is_staff=True, is_superuser=False).aggregate(total=Count("id"), active=Count("id", filter=Q(is_active=True)))
        response.data.update(total_staff=stats["total"], active_staff=stats["active"])
        return response

    def perform_destroy(self, instance):
        public_id = instance.avatar_public_id
        instance.delete()
        delete_image(public_id)
