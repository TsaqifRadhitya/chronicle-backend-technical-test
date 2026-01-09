from rest_framework.views import APIView
from rest_framework import status
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework.exceptions import ValidationError
from django.db.models import F
from .models import Product, Order, OrderDetail
from .serializers import ProductSerializer,OrderSerializer,CreateOrderSerializer

from .tasks import process_order
from utils.response import success_response,error_response
from http import HTTPStatus


class ProductAPIView(APIView):

    def get(self, request):
        data = cache.get("products")

        if not data:
            products = Product.objects.all()
            data = ProductSerializer(products, many=True).data
            cache.set("products", data)

        return success_response(
            data=data,
            message=HTTPStatus(status.HTTP_200_OK).phrase
        )

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        cache.delete("products")

        return success_response(
            data=serializer.data,
            message=HTTPStatus(status.HTTP_201_CREATED).phrase,
            status_code=status.HTTP_201_CREATED
        )

class ProductDetailAPIView(APIView):

    def get(self, request, pk):
        cache_key = f"product:{pk}"
        data = cache.get(cache_key)

        if not data:
            product = get_object_or_404(Product, pk=pk)
            data = ProductSerializer(product).data
            cache.set(cache_key, data)

        return success_response(
            data=data,
            message=HTTPStatus(status.HTTP_200_OK).phrase
        )

    def put(self, request, pk):
        product = get_object_or_404(Product, pk=pk)

        serializer = ProductSerializer(product, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        cache.delete(f"product:{pk}")
        cache.delete("products")

        return success_response(
            data=serializer.data,
            message=HTTPStatus(status.HTTP_200_OK).phrase
        )

    def delete(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        product.delete()

        cache.delete(f"product:{pk}")
        cache.delete("products")

        return success_response(
            message=HTTPStatus(status.HTTP_204_NO_CONTENT).phrase,
            status_code=status.HTTP_204_NO_CONTENT
        )

class OrderAPIView(APIView):

    @transaction.atomic
    def post(self, request):
        input_serializer = CreateOrderSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        order = Order.objects.create()

        for item in input_serializer.validated_data["items"]:
            product = get_object_or_404(
                Product.objects.select_for_update(),
                pk=item["product_id"]
            )

            quantity = item["quantity"]

            if product.stock < quantity:
                raise ValidationError({
                    "detail": f"Insufficient stock for product '{product.name}'."
                })

            OrderDetail.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=product.price
            )
            cache.delete(f"product:{product.id}")

            product.stock -= quantity
            product.save(update_fields=["stock"])

        process_order.apply_async(args=[order.id], countdown=5)
        cache.delete("products")
        cache.delete("orders")
        
        return success_response(
            data=OrderSerializer(order).data,
            message=HTTPStatus(status.HTTP_201_CREATED).phrase,
            status_code=status.HTTP_201_CREATED
        )

    def get(self, request):
        data = cache.get("orders")
        if not data:
            orders = Order.objects.all().prefetch_related("order_details__product")
            data = OrderSerializer(orders, many=True).data
            cache.set("orders",data)
        return success_response(
            data=data,
            message=HTTPStatus(status.HTTP_200_OK).phrase
        )

class OrderDetailApiView(APIView):
    def get(self,request,pk):
        data = cache.get(f"order:{pk}")
        if not data:
            order = get_object_or_404(Order.objects.prefetch_related("order_details__product"),pk=pk)
            data = OrderSerializer(order).data
            cache.set(f"order:{pk}",data)
        
        return success_response(data=data,message=HTTPStatus(status.HTTP_200_OK).phrase)
    
    @transaction.atomic
    def delete(self,request,pk):
        try:
            order = Order.objects.prefetch_related('order_details__product').select_for_update().get(pk=pk)
        except Order.DoesNotExist:
            return error_response(None,HTTPStatus(status.HTTP_404_NOT_FOUND).phrase,status.HTTP_404_NOT_FOUND)
        
        for item in order.order_details.all():
            product = item.product
            product.stock = F('stock') + item.quantity
            product.save()
            cache.delete(f"product:{product.id}")
            
        order.delete()
        
        cache.delete(f"order:{pk}")
        cache.delete("orders")
        cache.delete("products")
        
        return success_response(status_code=status.HTTP_204_NO_CONTENT,message=HTTPStatus(status.HTTP_204_NO_CONTENT))