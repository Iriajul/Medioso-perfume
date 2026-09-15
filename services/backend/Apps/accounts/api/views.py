from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView


class AdminLoginSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        if not self.user.is_staff:
            raise AuthenticationFailed("No active admin account found with the given credentials.")
        return data


class AdminLoginView(TokenObtainPairView):
    """Email + password login for dashboard admins. Returns access/refresh JWTs."""

    serializer_class = AdminLoginSerializer
    throttle_scope = "auth"
