from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from accounts.models import *


class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ("id","phone_number","first_name","last_name", "is_superuser", 
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



class NurseProfilesAdmin(admin.ModelAdmin):
    list_display = ['id',"average_rate","salary_per_hour" ,'is_working', 'balance']


admin.site.register(User, CustomUserAdmin)
# You can register additional profiles if necessary
admin.site.register(ClientProfile)
admin.site.register(NurseProfile, NurseProfilesAdmin)   # Same here
