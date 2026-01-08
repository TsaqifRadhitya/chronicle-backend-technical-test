from rest_framework import serializers
from .models import Order,OrderDetail,Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields  = "__all__"


class OrderDetailSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderDetail
        fields = "__all__"
        
class OrderSerializer(serializers.ModelSerializer):
    order_details = OrderDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ("id" , "order_details","created_at","updated_at")

class OrderItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)

    def validate_product_id(self, value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError("Product not found")
        return value


class CreateOrderSerializer(serializers.Serializer):
    items = OrderItemSerializer(many=True)

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("Items cannot be empty")
        return value