"""Customer app: branch locator."""

from django.db.models import FloatField, Value
from django.db.models.functions import Cast, Power
from rest_framework import filters, serializers, viewsets
from rest_framework.permissions import AllowAny

from Apps.branches.models import Branch


class AppBranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = ["id", "name", "is_flagship", "address", "city", "country", "phone", "email",
                  "weekday_opens", "weekday_closes", "sunday_opens", "sunday_closes", "latitude", "longitude", "image_url"]


class BranchViewSet(viewsets.ReadOnlyModelViewSet):
    """`?search=` city/street/name. `?lat=&lng=` sorts nearest first (branches with coordinates only)."""

    serializer_class = AppBranchSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "city", "country", "address"]

    def get_queryset(self):
        queryset = Branch.objects.all()
        try:
            lat, lng = float(self.request.query_params["lat"]), float(self.request.query_params["lng"])
        except (KeyError, ValueError):
            return queryset.order_by("-is_flagship", "name")
        # Squared degree distance is enough to rank nearby boutiques.
        distance = Power(Cast("latitude", FloatField()) - Value(lat), 2) + Power(Cast("longitude", FloatField()) - Value(lng), 2)
        return queryset.exclude(latitude=None).annotate(distance=distance).order_by("distance")
