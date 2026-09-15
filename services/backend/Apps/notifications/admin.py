from django.contrib import admin

from Apps.notifications.models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ["title", "audience", "recipients_count", "status", "created_at"]
