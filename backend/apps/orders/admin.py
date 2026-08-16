from django.contrib import admin

from .models import Customer, Order, OrderItem


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "email", "is_active")
    search_fields = ("name", "phone", "email")
    ordering = ("name",)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_number", "branch", "status", "order_type", "total", "ordered_at")
    list_filter = ("branch", "status", "order_type")
    search_fields = ("order_number",)
    ordering = ("-ordered_at",)
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "product", "quantity", "unit_price", "total")
    list_filter = ("product",)
    search_fields = ("order__order_number", "product__name")
