# views.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Category, Order, Product
from .permissions import IsAuthorOrReadOnlyPermission
from .serializers import CategorySerializer, OrderSerializer, ProductSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()

class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    permission_classes = (IsAuthenticated,)