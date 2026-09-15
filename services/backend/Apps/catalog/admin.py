from django.contrib import admin

from Apps.catalog.models import Banner, Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "type", "created_at"]
    list_filter = ["type"]
    search_fields = ["name"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "price", "stock", "is_featured"]
    list_filter = ["category", "is_featured"]
    list_select_related = ["category"]
    search_fields = ["name"]


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ["title", "starts_on", "ends_on", "is_active"]
