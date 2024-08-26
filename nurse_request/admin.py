from django.contrib import admin
from .models import Request  # Assuming your model is in the same app


class RequestAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "client",
        "nurse",
        "request_for_date",
        "status",
        "created_date",
    )
    list_filter = ("status", "client", "nurse")
    search_fields = (
        "client__user__username",
        "client__user__first_name",
        "client__user__last_name",
    )  # Search by client details


admin.site.register(Request, RequestAdmin)
