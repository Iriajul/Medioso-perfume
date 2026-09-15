from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import serializers, status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from rest_framework_simplejwt.views import TokenObtainPairView

from Apps.accounts.models import User


class AdminLoginSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        # Display claims so the dashboard header needs no extra API call.
        token = super().get_token(user)
        token["full_name"] = user.full_name
        token["email"] = user.email
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        if not self.user.is_staff:
            raise AuthenticationFailed("No active admin account found with the given credentials.")
        return data


class AdminLoginView(TokenObtainPairView):
    """Email + password login for dashboard admins. Returns access/refresh JWTs."""

    serializer_class = AdminLoginSerializer
    throttle_scope = "auth"


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetRequestView(APIView):
    """Emails an admin a reset link. Always 204 so emails can't be enumerated."""

    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_scope = "auth"

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.filter(
            email__iexact=serializer.validated_data["email"], is_staff=True, is_active=True
        ).first()
        if user:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            link = f"{settings.ADMIN_URL}/reset-password?uid={uid}&token={token}"
            context = {"name": user.full_name, "link": link, "logo_url": f"{settings.ADMIN_URL}/logo.png"}
            send_mail(
                "Reset your Mad Perfume admin password",
                f"Use this link to set a new password:\n\n{link}\n\n"
                "The link expires in 1 hour. If you didn't request this, you can ignore this email.",
                None,
                [user.email],
                html_message=render_to_string("accounts/emails/password_reset.html", context),
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        try:
            user = User.objects.get(pk=urlsafe_base64_decode(attrs["uid"]).decode(), is_active=True)
        except (User.DoesNotExist, ValueError, TypeError, OverflowError):
            user = None
        if user is None or not default_token_generator.check_token(user, attrs["token"]):
            raise serializers.ValidationError({"token": "This reset link is invalid or has expired."})
        try:
            validate_password(attrs["password"], user)
        except DjangoValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})
        attrs["user"] = user
        return attrs


class PasswordResetConfirmView(APIView):
    """Sets the new password and signs the admin out everywhere."""

    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_scope = "auth"

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        user.set_password(serializer.validated_data["password"])
        user.save(update_fields=["password"])
        BlacklistedToken.objects.bulk_create(
            [BlacklistedToken(token=t) for t in OutstandingToken.objects.filter(user=user).only("id")],
            ignore_conflicts=True,
        )
        return Response(status=status.HTTP_204_NO_CONTENT)
