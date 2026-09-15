from django.contrib import admin

from Apps.branches.models import Branch


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ["name", "phone", "created_at"]
    search_fields = ["name", "address"]
