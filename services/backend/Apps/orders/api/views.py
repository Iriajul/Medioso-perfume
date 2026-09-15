from decimal import Decimal

from django.conf import settings
from django.db import transaction
from django.db.models import Count, F, Q, Sum
from rest_framework import mixins, serializers, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from Apps.accounts.models import User
from Apps.branches.models import Branch
from Apps.catalog.models import Product
from Apps.common.stats import last_30_days_filters, money, trend_percent
from Apps.loyalty import services as loyalty
from Apps.notifications.models import UserNotification
from Apps.orders.models import Order, OrderStatusEvent

REVENUE_EXCLUDES = Q(status=Order.Status.CANCELLED)
ORDER_MESSAGES = {
    Order.Status.PROCESSING: ("Your order is being prepared", "Order {order.number} is being prepared by our atelier."),
    Order.Status.SHIPPED: ("Your signature scent is in transit", "Order {order.number} has shipped. Expected delivery: {order.estimated_delivery:%b %d}."),
    Order.Status.DELIVERED: ("Order delivered", "Order {order.number} has been delivered. Enjoy your fragrance."),
    Order.Status.CANCELLED: ("Order cancelled", "Order {order.number} has been cancelled."),
}


class OrderListSerializer(serializers.ModelSerializer):
    number = serializers.CharField(read_only=True)
    customer_name = serializers.CharField(source="customer.full_name")
    customer_email = serializers.CharField(source="customer.email")

    class Meta:
        model = Order
        fields = ["id", "number", "customer_name", "customer_email", "total", "status", "channel", "created_at"]


class OrderDetailSerializer(serializers.ModelSerializer):
    number = serializers.CharField(read_only=True)
    customer = serializers.SerializerMethodField()
    branch_name = serializers.CharField(source="branch.name", default=None)
    items = serializers.SerializerMethodField()
    events = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "id", "number", "status", "channel", "branch_name", "created_at", "customer", "items", "events",
            "subtotal", "shipping_method", "shipping_fee", "tax", "total",
            "payment_method", "payment_reference", "card_last4", "shipping_address", "billing_address", "notes",
        ]

    def get_customer(self, order):
        c = order.customer
        return {"id": c.id, "full_name": c.full_name, "email": c.email, "phone": c.phone}

    def get_items(self, order):
        return [
            {"product_name": i.product_name, "sku": i.sku, "image_url": i.image_url, "unit_price": str(i.unit_price),
             "quantity": i.quantity, "line_total": str(i.line_total)}
            for i in order.items.all()
        ]

    def get_events(self, order):
        return [{"status": e.status, "created_at": e.created_at} for e in order.events.all()]


class InStorePurchaseSerializer(serializers.Serializer):
    customer = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(is_staff=False, is_active=True))
    branch = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.all())
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal("0.01"))
    notes = serializers.CharField(required=False, allow_blank=True)


class OrderViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, GenericViewSet):
    permission_classes = [IsAdminUser]
    pagination_class = type("OrderPagination", (PageNumberPagination,), {"page_size": 5})

    def get_queryset(self):
        if self.action == "retrieve":
            return Order.objects.select_related("customer", "branch").prefetch_related("items", "events")
        return Order.objects.select_related("customer")

    def get_serializer_class(self):
        return OrderDetailSerializer if self.action == "retrieve" else OrderListSerializer

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        current, previous = last_30_days_filters()
        stats = Order.objects.exclude(REVENUE_EXCLUDES).aggregate(
            revenue=Sum("total"),
            current=Sum("total", filter=current),
            previous=Sum("total", filter=previous),
            active=Count("id", filter=Q(status__in=Order.ACTIVE_STATUSES)),
        )
        response.data.update(
            total_revenue=money(stats["revenue"]),
            revenue_trend=trend_percent(stats["current"] or 0, stats["previous"] or 0),
            active_orders=stats["active"],
        )
        return response

    @action(detail=True, methods=["post"], url_path="status")
    def update_status(self, request, pk=None):
        order = self.get_object()
        new_status = request.data.get("status")
        allowed = [s for s in Order.Status.values if s != Order.Status.IN_STORE]
        if order.channel != Order.Channel.APP or new_status not in allowed:
            raise serializers.ValidationError({"status": "Invalid status for this order."})
        if new_status != order.status:
            with transaction.atomic():
                if new_status == Order.Status.CANCELLED:
                    # Put the units back on sale.
                    for item in order.items.exclude(product=None):
                        Product.objects.filter(pk=item.product_id).update(stock=F("stock") + item.quantity)
                order.status = new_status
                order.save(update_fields=["status", "updated_at"])
                OrderStatusEvent.objects.create(order=order, status=new_status)
                if message := ORDER_MESSAGES.get(new_status):
                    UserNotification.objects.create(
                        user_id=order.customer_id, category=UserNotification.Category.ORDERS, order=order,
                        title=message[0], body=message[1].format(order=order),
                    )
                if new_status == Order.Status.DELIVERED:
                    loyalty.earn_for_order(order, created_by=request.user)
        return Response(OrderDetailSerializer(self.get_queryset().get(pk=order.pk)).data)

    @action(detail=False, methods=["post"], url_path="in-store")
    def register_in_store(self, request):
        """Registers a branch purchase and awards its points immediately."""
        data = InStorePurchaseSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        v = data.validated_data
        with transaction.atomic():
            order = Order.objects.create(
                customer=v["customer"], channel=Order.Channel.BRANCH, branch=v["branch"], status=Order.Status.IN_STORE,
                subtotal=v["amount"], total=v["amount"], payment_method=Order.PaymentMethod.IN_STORE,
                notes=v.get("notes", ""), created_by=request.user,
            )
            OrderStatusEvent.objects.create(order=order, status=order.status)
            entry = loyalty.earn_for_order(order, created_by=request.user)
        return Response(
            {"order": order.number, "points": entry.points if entry else 0, "balance": entry.balance_after if entry else v["customer"].points_balance},
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, url_path="in-store/recent", pagination_class=None)
    def recent_in_store(self, request):
        orders = (
            Order.objects.filter(channel=Order.Channel.BRANCH)
            .select_related("customer")
            .annotate(points=Sum("loyalty_transactions__points", filter=Q(loyalty_transactions__kind="earned")))
            .order_by("-created_at")[:5]  # aggregate queries drop Meta.ordering
        )
        return Response({
            "points_per_dollar": settings.POINTS_PER_DOLLAR_BRANCH,
            "results": [
                {"id": o.id, "number": o.number, "customer_name": o.customer.full_name, "total": str(o.total),
                 "points": o.points or 0, "created_at": o.created_at}
                for o in orders
            ],
        })
