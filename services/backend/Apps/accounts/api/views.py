from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.http import urlsafe_base64_decode
from rest_framework import serializers, status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from rest_framework_simplejwt.views import TokenObtainPairView

from Apps.accounts.emails import send_password_link
from Apps.accounts.models import User


def check_password_rules(password, user):
    try:
        validate_password(password, user)
    except DjangoValidationError as e:
        raise serializers.ValidationError({"password": list(e.messages)})


def revoke_sessions(user):
    """Blacklists every refresh token issued to the user (signs them out everywhere)."""
    BlacklistedToken.objects.bulk_create(
        [BlacklistedToken(token=t) for t in OutstandingToken.objects.filter(user=user).only("id")],
        ignore_conflicts=True,
    )


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
            send_password_link(user)
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
        check_password_rules(attrs["password"], user)
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
        user.save(update_fields=["password", "password_changed_at"])
        revoke_sessions(user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = self.context["request"].user
        if not user.check_password(attrs["current_password"]):
            raise serializers.ValidationError({"current_password": "Current password is incorrect."})
        if attrs["current_password"] == attrs["password"]:
            raise serializers.ValidationError({"password": "New password must be different from the current one."})
        check_password_rules(attrs["password"], user)
        return attrs


class MeView(APIView):
    """Signed-in admin's account info."""

    permission_classes = [IsAdminUser]

    def get(self, request):
        u = request.user
        return Response({"id": u.id, "full_name": u.full_name, "email": u.email, "password_changed_at": u.password_changed_at})


class ChangePasswordView(APIView):
    """Security Settings: change password, then sign out all sessions."""

    permission_classes = [IsAdminUser]
    throttle_scope = "auth"

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data["password"])
        request.user.save(update_fields=["password", "password_changed_at"])
        revoke_sessions(request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)
