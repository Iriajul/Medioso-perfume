"""Customer app: cart, checkout, orders and the Stripe webhook."""

from decimal import ROUND_HALF_UP, Decimal

import stripe
from django.conf import settings
from django.db import IntegrityError, transaction
from django.db.models import F, Sum
from rest_framework import generics, mixins, serializers, status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from Apps.catalog.models import Product
from Apps.orders.emails import send_invoice
from Apps.orders.models import CartItem, Order, OrderItem, OrderStatusEvent

CENTS = Decimal("0.01")


def product_image(product):
    return next((img["url"] for img in product.images if img), "")


# ─── Cart ──────────────────────────────────────────────────────────────


class CartItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    name = serializers.CharField(source="product.name", read_only=True)
    variant = serializers.SerializerMethodField()
    price = serializers.DecimalField(source="product.price", max_digits=10, decimal_places=2, read_only=True)
    image_url = serializers.SerializerMethodField()
    line_total = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ["id", "product", "name", "variant", "price", "image_url", "quantity", "line_total"]

    def get_variant(self, item):
        return variant_label(item.product)

    def get_image_url(self, item):
        return product_image(item.product)

    def get_line_total(self, item):
        return str(item.product.price * item.quantity)

    def validate(self, attrs):
        product = attrs.get("product") or self.instance.product
        existing = 0 if self.instance or not attrs.get("product") else (
            CartItem.objects.filter(user=self.context["request"].user, product=product).values_list("quantity", flat=True).first() or 0)
        if existing + attrs.get("quantity", 1) > product.stock:
            raise serializers.ValidationError({"quantity": f"Only {product.stock} left in stock."})
        return attrs


def variant_label(product):
    return " / ".join(filter(None, [product.size, product.get_concentration_display()]))


class CartViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """GET the cart with subtotal; POST {product, quantity} adds (or increases); PATCH {quantity}; DELETE removes."""

    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None
    http_method_names = ["get", "post", "patch", "delete"]

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user).select_related("product")

    def list(self, request, *args, **kwargs):
        items = self.get_serializer(self.get_queryset(), many=True).data
        subtotal = sum((Decimal(i["line_total"]) for i in items), Decimal("0"))
        return Response({"items": items, "items_count": sum(i["quantity"] for i in items), "subtotal": str(subtotal)})

    def perform_create(self, serializer):
        data = serializer.validated_data
        item, created = CartItem.objects.get_or_create(user=self.request.user, product=data["product"], defaults={"quantity": data.get("quantity", 1)})
        if not created:
            CartItem.objects.filter(pk=item.pk).update(quantity=F("quantity") + data.get("quantity", 1))
            item.refresh_from_db()
        serializer.instance = item


# ─── Checkout ──────────────────────────────────────────────────────────


class CheckoutSerializer(serializers.Serializer):
    shipping_name = serializers.CharField(max_length=255)
    shipping_address = serializers.CharField()
    shipping_city = serializers.CharField(max_length=100)
    shipping_phone = serializers.CharField(max_length=30, required=False, allow_blank=True)
    payment_method = serializers.ChoiceField(choices=[Order.PaymentMethod.CARD, Order.PaymentMethod.COD])


class OrderItemSerializer(serializers.ModelSerializer):
    line_total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ["product", "product_name", "variant", "image_url", "unit_price", "quantity", "line_total"]


class OrderEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderStatusEvent
        fields = ["status", "created_at"]


class AppOrderSerializer(serializers.ModelSerializer):
    number = serializers.CharField(read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    events = OrderEventSerializer(many=True, read_only=True)
    estimated_delivery = serializers.DateField(read_only=True)
    branch_name = serializers.CharField(source="branch.name", default=None)

    class Meta:
        model = Order
        fields = [
            "id", "number", "status", "channel", "branch_name", "created_at", "estimated_delivery", "items", "events",
            "subtotal", "shipping_fee", "tax", "total", "payment_method", "card_last4",
            "shipping_name", "shipping_address", "shipping_city", "shipping_phone",
        ]


class OrderViewSet(mixins.CreateModelMixin, viewsets.ReadOnlyModelViewSet):
    """Order history, tracking detail, and checkout (POST turns the cart into an order).
    Card orders return a Stripe `client_secret` for the app's payment sheet.
    Send an `Idempotency-Key` header (e.g. a UUID per checkout attempt): retries with it return the same order."""

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (Order.objects.filter(customer=self.request.user)
                .select_related("branch").prefetch_related("items", "events"))

    def get_serializer_class(self):
        return CheckoutSerializer if self.action == "create" else AppOrderSerializer

    def create(self, request, *args, **kwargs):
        data = self.get_serializer(data=request.data)
        data.is_valid(raise_exception=True)
        key = request.headers.get("Idempotency-Key", "")[:64]
        order = self.get_queryset().filter(idempotency_key=key).first() if key else None
        created = order is None
        if created:
            try:
                order = self.place_order(request.user, data.validated_data, key)
            except IntegrityError:  # a concurrent retry with the same key won the race
                order, created = self.get_queryset().get(idempotency_key=key), False

        client_secret = None
        if order.payment_method == Order.PaymentMethod.CARD and order.status == Order.Status.PENDING_PAYMENT:
            # Stripe's own idempotency key: a retry gets the same PaymentIntent back.
            intent = stripe.PaymentIntent.create(
                api_key=settings.STRIPE_SECRET_KEY, amount=int(order.total * 100), currency="usd",
                metadata={"order_id": order.pk}, automatic_payment_methods={"enabled": True},
                idempotency_key=f"order-{order.pk}-payment",
            )
            Order.objects.filter(pk=order.pk).update(payment_reference=intent.id)
            client_secret = intent.client_secret

        order = self.get_queryset().get(pk=order.pk)
        return Response({**AppOrderSerializer(order).data, "client_secret": client_secret},
                        status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    @staticmethod
    @transaction.atomic
    def place_order(user, data, idempotency_key=""):
        cart = list(CartItem.objects.filter(user=user).select_related("product"))
        if not cart:
            raise serializers.ValidationError({"detail": "Your cart is empty."})
        # Lock the products so two checkouts can't oversell the last unit.
        products = Product.objects.select_for_update().in_bulk([i.product_id for i in cart])
        for item in cart:
            if products[item.product_id].stock < item.quantity:
                raise serializers.ValidationError({"detail": f"{item.product.name}: only {products[item.product_id].stock} left in stock."})

        subtotal = sum((i.product.price * i.quantity for i in cart), Decimal("0"))
        tax = (subtotal * Decimal(settings.TAX_RATE)).quantize(CENTS, ROUND_HALF_UP)
        shipping = Decimal(settings.SHIPPING_FEE)
        cod = data["payment_method"] == Order.PaymentMethod.COD
        order = Order.objects.create(
            customer=user, channel=Order.Channel.APP, subtotal=subtotal, tax=tax, shipping_fee=shipping, total=subtotal + tax + shipping,
            status=Order.Status.PROCESSING if cod else Order.Status.PENDING_PAYMENT, payment_method=data["payment_method"],
            shipping_name=data["shipping_name"], shipping_address=data["shipping_address"], shipping_city=data["shipping_city"],
            shipping_phone=data.get("shipping_phone") or user.phone, idempotency_key=idempotency_key,
        )
        OrderItem.objects.bulk_create(OrderItem(
            order=order, product=i.product, product_name=i.product.name, variant=variant_label(i.product), sku=i.product.sku,
            image_url=product_image(i.product), unit_price=i.product.price, quantity=i.quantity,
        ) for i in cart)
        for item in cart:
            Product.objects.filter(pk=item.product_id).update(stock=F("stock") - item.quantity)
        OrderStatusEvent.objects.bulk_create(
            [OrderStatusEvent(order=order, status=Order.Status.PENDING_PAYMENT)]
            + ([OrderStatusEvent(order=order, status=Order.Status.PROCESSING)] if cod else [])
        )
        CartItem.objects.filter(user=user).delete()
        if cod:
            transaction.on_commit(lambda: send_invoice(order.pk))
        return order


# ─── Stripe webhook ────────────────────────────────────────────────────


class StripeWebhookView(generics.GenericAPIView):
    """Marks card orders paid when Stripe confirms the payment."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        try:
            event = stripe.Webhook.construct_event(request.body, request.headers.get("Stripe-Signature", ""), settings.STRIPE_WEBHOOK_SECRET)
        except (ValueError, stripe.SignatureVerificationError):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if event["type"] == "payment_intent.succeeded":
            intent = event["data"]["object"]
            with transaction.atomic():
                order = Order.objects.select_for_update().filter(payment_reference=intent["id"], status=Order.Status.PENDING_PAYMENT).first()
                if order:
                    method = stripe.PaymentMethod.retrieve(intent["payment_method"], api_key=settings.STRIPE_SECRET_KEY)
                    order.status = Order.Status.PAID
                    order.card_last4 = method.card.last4 if method.get("card") else ""
                    order.save(update_fields=["status", "card_last4", "updated_at"])
                    OrderStatusEvent.objects.create(order=order, status=Order.Status.PAID)
                    transaction.on_commit(lambda: send_invoice(order.pk))
        return Response({"received": True})
