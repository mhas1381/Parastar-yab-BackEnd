from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from accounts.models import *


class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ("phone_number","first_name","last_name","otp" , "count" , "logged", "is_superuser", "is_active",
                    "is_verified", "role", "national_id")
    list_filter = ("is_superuser", "is_active", "is_verified", "role")
    search_fields = ("phone_number",)
    ordering = ("phone_number",)

    fieldsets = (
        ("Authentication", {"fields": ("phone_number","otp", "password")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_staff",
                    "is_active",
                    "is_superuser",
                    "is_verified",
                )
            },
        ),
        ("Role", {"fields": ("role",)}),
        ("group permissions", {"fields": ("groups", "user_permissions")}),
        ("important date", {"fields": ("last_login",)}),
        ("Additional Information", {
         "fields": ("national_id", "avatar", "national_card_image","first_name","last_name")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "phone_number",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_active",
                    "is_superuser",
                    "is_verified",
                    "role",
                    "national_id",  # اضافه کردن این فیلد
                    "avatar",        # اضافه کردن دیگر فیلدهای لازم
                    "national_card_image",
                ),
            },
        ),
    )



# class NurseProfilesAdmin(admin)
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        # You may want to filter queryset by role, if needed
        return queryset


admin.site.register(User, CustomUserAdmin)
# You can register additional profiles if necessary
admin.site.register(ClientProfile)
admin.site.register(NurseProfile)   # Same here
