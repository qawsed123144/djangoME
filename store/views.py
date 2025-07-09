from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.viewsets import ModelViewSet
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import action
from rest_framework.decorators import api_view, permission_classes

from .models import Collection, Product, Cart, CartItem, Order, OrderItem, Review, Customer, ProductImage, Address
from .serializers import CollectionSerializer, ProductSerializer, ReviewSerializer, CartSerializer, CartItemSerializer, OrderSerializer, OrderCreateSerializer, ProductImageSerializer, AddressSerializer, CustomerSerializer
from pyshop.permission import IsAdminOrReadOnly


class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.prefetch_related(
        "product_set__productimage_set"  # 預載該 Collection 內的產品與產品圖片
    )
    serializer_class = CollectionSerializer
    permission_classes = [IsAdminOrReadOnly]


def destroy(self, request, *args, **kwargs):
    def destroy(self, request, *args, **kwargs):
        if Product.objects.filter(collection_id=kwargs['pk']).count() > 0:
            return Response({'error': "cannot be deleted"},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(request, *args, **kwargs)


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.prefetch_related('productimage_set').all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]

    def destroy(self, request, *args, **kwargs):
        if OrderItem.objects.filter(product_id=kwargs['pk']).count() > 0:
            return Response({'error': "cannot be deleted"},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(request, *args, **kwargs)


class ProductImageViewSet(ModelViewSet):
    def get_queryset(self):
        return ProductImage.objects.filter(product_id=self.kwargs['product_pk'])

    def get_serializer_context(self):
        return {'product_id': self.kwargs['product_pk']}

    serializer_class = ProductImageSerializer


class ReviewViewSet(ModelViewSet):
    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs['product_pk'])

    def get_serializer_context(self):
        return {'product_id': self.kwargs['product_pk']}

    serializer_class = ReviewSerializer


class CartViewSet(ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Cart.objects.none()
        return Cart.objects.prefetch_related('cartitem_set__product').filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        user = request.user
        existing_cart = Cart.objects.filter(user=user).first()
        if existing_cart:
            serializer = self.get_serializer(existing_cart)
            return Response(serializer.data, status=status.HTTP_200_OK)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CartItemViewSet(ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        return {'cart_id': self.kwargs['cart_pk']}

    def get_queryset(self):
        cart_id = self.kwargs['cart_pk']
        user = self.request.user

        cart_qs = Cart.objects.filter(id=cart_id, user=user)
        if not cart_qs.exists():
            raise PermissionDenied("您無權存取此購物車")

        return CartItem.objects.filter(cart_id=cart_id).select_related('product')

    serializer_class = CartItemSerializer


class OrderViewSet(ModelViewSet):
    serializer_class = OrderSerializer

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Order.objects.none()
        return Order.objects.prefetch_related('orderitem_set__product').select_related('shipping_address').filter(customer_id=user.id)

    def create(self, request, *args, **kwargs):
        create_serializer = OrderCreateSerializer(
            data=request.data, context={'customer_id': request.user.id})
        create_serializer.is_valid(raise_exception=True)
        order = create_serializer.save()

        response_serializer = self.get_serializer(order)
        headers = self.get_success_headers(response_serializer.data)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def retrieve(self, request, *args, **kwargs):
        """覆蓋 retrieve，避免別人亂打別人的訂單"""
        try:
            order = self.get_queryset().get(pk=kwargs['pk'])
        except Order.DoesNotExist:
            return Response({"detail": "找不到訂單或無權限查看"}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(order)
        return Response(serializer.data)

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]


class AddressViewSet(ModelViewSet):
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # 僅顯示登入使用者的地址
        return Address.objects.filter(customer=self.request.user)

    def perform_create(self, serializer):
        # 建立時自動綁定目前使用者
        serializer.save(customer=self.request.user)
