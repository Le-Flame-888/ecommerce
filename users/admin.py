from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Address

class AddressInline(admin.StackedInline):
    model = Address
    extra = 1

class CustomUserAdmin(UserAdmin):
    inlines = [AddressInline]
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('phone_number',)}),
    )

admin.site.register(User, CustomUserAdmin)
admin.site.register(Address)
