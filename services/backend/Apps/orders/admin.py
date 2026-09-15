from django.contrib import admin

from Apps.orders.models import Order, OrderItem, OrderStatusEvent


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


class OrderStatusEventInline(admin.TabularInline):
    model = OrderStatusEvent
    extra = 0
    readonly_fields = ["status", "created_at"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "customer", "channel", "status", "total", "created_at"]
    list_filter = ["channel", "status"]
    list_select_related = ["customer"]
    inlines = [OrderItemInline, OrderStatusEventInline]
