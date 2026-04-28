from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['variant']
    extra = 0
    readonly_fields = ['price', 'quantity', 'get_cost']

    def get_cost(self, obj):
        return obj.get_cost()
    get_cost.short_description = 'Coût total'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'first_name', 'last_name', 'email', 'city', 'status', 'total_amount', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['first_name', 'last_name', 'email', 'city']
    list_editable = ['status']
    inlines = [OrderItemInline]
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
