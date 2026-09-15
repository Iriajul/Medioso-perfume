"""Customer app: registration, login, password reset by code, profile, devices."""

import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Q
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import generics, serializers, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from Apps.accounts.api.views import AdminLoginSerializer, ChangePasswordView, check_password_rules
from Apps.accounts.models import DeviceToken, PasswordResetCode, User
from Apps.common.media import delete_image, upload_image, validate_image
from Apps.loyalty.services import tier_for

CODE_TTL_MINUTES = 10


def tokens_for(user):
    refresh = AdminLoginSerializer.get_token(user)  # same name/email claims as the dashboard
    return {"access": str(refresh.access_token), "refresh": str(refresh)}


# ─── Register / login ──────────────────────────────────────────────────


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    phone = serializers.CharField(max_length=30)

    class Meta:
        model = User
        fields = ["full_name", "email", "phone", "password"]

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return value.lower()

    def validate_phone(self, value):
        if User.objects.filter(phone=value).exists():
            raise serializers.ValidationError("An account with this phone number already exists.")
        return value

    def validate(self, attrs):
        check_password_rules(attrs["password"], User(email=attrs["email"], full_name=attrs["full_name"]))
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_scope = "auth"

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(tokens_for(serializer.save()), status=status.HTTP_201_CREATED)


class LoginSerializer(serializers.Serializer):
    identifier = serializers.CharField(help_text="Email address or phone number")
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        value = attrs["identifier"].strip()
        user = User.objects.filter(Q(email__iexact=value) | Q(phone=value), is_active=True).first()
        if not user or not user.check_password(attrs["password"]):
            raise serializers.ValidationError({"detail": "Invalid email/phone or password."})
        attrs["user"] = user
        return attrs


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_scope = "auth"

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        User.objects.filter(pk=user.pk).update(last_login=timezone.now())
        return Response(tokens_for(user))


# ─── Password reset by 6-digit code ────────────────────────────────────


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ResetCodeRequestView(generics.GenericAPIView):
    """Emails a 6-digit code. Always 204 so emails can't be enumerated."""

    serializer_class = EmailSerializer
    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_scope = "auth"

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.filter(email__iexact=serializer.validated_data["email"], is_active=True).first()
        if user:
            code = f"{secrets.randbelow(1_000_000):06d}"
            PasswordResetCode.objects.filter(user=user).delete()
            PasswordResetCode.objects.create(
                user=user, code_hash=make_password(code), expires_at=timezone.now() + timedelta(minutes=CODE_TTL_MINUTES)
            )
            context = {"name": user.full_name, "code": code, "minutes": CODE_TTL_MINUTES, "logo_url": f"{settings.ADMIN_URL}/logo.png"}
            send_mail(
                "Your Mad Perfume verification code",
                f"Your verification code is {code}. It expires in {CODE_TTL_MINUTES} minutes.",
                None,
                [user.email],
                html_message=render_to_string("accounts/emails/reset_code.html", context),
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class ResetCodeVerifySerializer(EmailSerializer):
    code = serializers.RegexField(r"^\d{6}$")


class ResetCodeVerifyView(generics.GenericAPIView):
    """Exchanges a valid code for {uid, token}, used with auth/password-reset/confirm/."""

    serializer_class = ResetCodeVerifySerializer
    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_scope = "auth"

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        entry = PasswordResetCode.objects.filter(
            user__email__iexact=serializer.validated_data["email"], expires_at__gt=timezone.now(),
            attempts__lt=PasswordResetCode.MAX_ATTEMPTS,
        ).select_related("user").first()
        if not entry or not check_password(serializer.validated_data["code"], entry.code_hash):
            if entry:
                PasswordResetCode.objects.filter(pk=entry.pk).update(attempts=entry.attempts + 1)
            raise serializers.ValidationError({"code": "Invalid or expired code."})
        entry.delete()
        user = entry.user
        return Response({"uid": urlsafe_base64_encode(force_bytes(user.pk)), "token": default_token_generator.make_token(user)})


# ─── Profile ───────────────────────────────────────────────────────────


class ProfileSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(write_only=True, required=False, validators=[validate_image])
    tier = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id", "full_name", "email", "phone", "shipping_address", "avatar", "avatar_url", "language",
            "push_enabled", "notify_collections", "notify_rewards", "notify_orders", "points_balance", "tier",
        ]
        read_only_fields = ["avatar_url", "points_balance"]

    def get_tier(self, user):
        return tier_for(user.lifetime_points)

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exclude(pk=self.instance.pk).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return value.lower()

    def validate_phone(self, value):
        if value and User.objects.filter(phone=value).exclude(pk=self.instance.pk).exists():
            raise serializers.ValidationError("An account with this phone number already exists.")
        return value

    def update(self, instance, validated_data):
        old = None
        if avatar := validated_data.pop("avatar", None):
            old = instance.avatar_public_id
            validated_data["avatar_url"], validated_data["avatar_public_id"] = upload_image(avatar, "avatars")
        instance = super().update(instance, validated_data)
        delete_image(old)
        return instance


class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class AppChangePasswordView(ChangePasswordView):
    permission_classes = [IsAuthenticated]


class DeviceTokenSerializer(serializers.ModelSerializer):
    token = serializers.CharField(max_length=255)

    class Meta:
        model = DeviceToken
        fields = ["token", "platform"]


class DeviceTokenView(generics.CreateAPIView, generics.DestroyAPIView):
    """POST registers this device for push; DELETE (on logout) removes it."""

    serializer_class = DeviceTokenSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "token"

    def get_queryset(self):
        return DeviceToken.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # A token moves to whoever signed in on that device last.
        DeviceToken.objects.update_or_create(token=serializer.validated_data["token"], defaults={
            "user": self.request.user, "platform": serializer.validated_data["platform"],
        })
