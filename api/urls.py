from django.urls import path
from .views import ProductAPIView, ProductDetailAPIView,OrderAPIView

urlpatterns = [
    path("products/", ProductAPIView.as_view()),
    path("products/<int:pk>/", ProductDetailAPIView.as_view()),
    path("orders/", OrderAPIView.as_view()),
    path("orders/<int:pk>", OrderAPIView.as_view()),
]
