from rest_framework import serializers

from apps.branches.models import Branch
from apps.products.models import Product

from .models import Customer, Order, OrderItem


class BranchMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = ["id", "name", "code", "city"]


class CustomerMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ["id", "name", "phone", "email"]


class ProductMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "sku"]


class OrderListSerializer(serializers.ModelSerializer):
    branch = BranchMiniSerializer(read_only=True)
    customer = CustomerMiniSerializer(read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "order_number",
            "branch",
            "customer",
            "order_type",
            "status",
            "subtotal",
            "discount",
            "tax",
            "total",
            "ordered_at",
        ]


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductMiniSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "product", "quantity", "unit_price", "discount", "total"]


class OrderDetailSerializer(serializers.ModelSerializer):
    branch = BranchMiniSerializer(read_only=True)
    customer = CustomerMiniSerializer(read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "order_number",
            "branch",
            "customer",
            "order_type",
            "status",
            "ordered_at",
            "subtotal",
            "discount",
            "tax",
            "total",
            "items",
        ]
