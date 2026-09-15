from django.contrib import admin

from Apps.loyalty.models import LoyaltyTransaction, Reward


@admin.register(Reward)
class RewardAdmin(admin.ModelAdmin):
    list_display = ["name", "points_required", "category", "eligibility", "is_active"]


@admin.register(LoyaltyTransaction)
class LoyaltyTransactionAdmin(admin.ModelAdmin):
    list_display = ["customer", "kind", "channel", "points", "balance_after", "created_at"]
    list_filter = ["kind", "channel"]
    list_select_related = ["customer"]
    readonly_fields = [f.name for f in LoyaltyTransaction._meta.fields]
