from django.contrib import admin
from .models import User, Product, Order, Report
from django.contrib.auth.admin import UserAdmin

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Custom Fields", {"fields": ("role",)}),
    )

    def save_model(self, request, obj, form, change):
        if change and obj.password != User.objects.get(pk=obj.pk).password:
            obj.set_password(obj.password)
        super().save_model(request, obj, form, change)

admin.site.register(User, CustomUserAdmin)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(Report)