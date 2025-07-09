from django.db import transaction
from rest_framework import serializers
from .models import Collection, Product, Review, Cart, CartItem, Customer, Order, OrderItem, ProductImage, Address


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'city', 'street', 'zip']


class CustomerCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'email', 'first_name', 'last_name', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = Customer.objects.create_user(**validated_data)
        return user


class CustomerSerializer(serializers.ModelSerializer):
    addresses = AddressSerializer(
        many=True, source='address_set', read_only=True)

    class Meta:
        model = Customer
        fields = ['id', 'first_name', 'last_name',
                  'email', 'phone', 'birth_date', 'membership', 'addresses']


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image']

    def create(self, validated_data):
        product_id = self.context['product_id']
        return ProductImage.objects.create(product_id=product_id, **validated_data)


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'name', 'description', 'date']

    def create(self, validated_data):
        product_id = self.context['product_id']
        return Review.objects.create(product_id=product_id, **validated_data)


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'description',
                  'price', 'price_tax', 'inventory', 'collection', 'productimage_set']
    productimage_set = ProductImageSerializer(many=True, read_only=True)
    price_tax = serializers.SerializerMethodField(method_name='calculateTax')

    def calculateTax(self, product: Product):
        return product.price * 1.1


class CollectionSerializer(serializers.ModelSerializer):
    products = ProductSerializer(
        many=True, read_only=True, source="product_set")

    class Meta:
        model = Collection
        fields = ["id", "title", "products"]


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'total_price', 'product_title']
    product_title = serializers.ReadOnlyField(source="product.title")
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, cartitem: CartItem):
        return cartitem.quantity * cartitem.product.price

    def create(self, validated_data):
        # 從前端輸入的 product_id 查詢產品
        product = validated_data['product']
        quantity = validated_data['quantity']
        cart_id = self.context.get('cart_id')
        price = product.price

        cart_item, created = CartItem.objects.get_or_create(
            cart_id=cart_id,
            product=product,
            defaults={'quantity': quantity, 'price': price}
        )

        # 如果已經存在，則只增加數量
        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        return cart_item

    def update(self, instance, validated_data):
        instance.quantity = validated_data.get('quantity', instance.quantity)
        instance.save()
        return instance


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['id', 'user', 'cartitem_set', 'total_price']

    id = serializers.UUIDField(read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    cartitem_set = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, cart: Cart):
        return sum([i.quantity*i.product.price for i in cart.cartitem_set.all()])


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'total_price', 'product_title']
    product = ProductSerializer()
    product_title = serializers.ReadOnlyField(source="product.title")
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, orderitem: OrderItem):
        return orderitem.quantity * orderitem.product.price

    def create(self, validated_data):
        # 從前端輸入的 product_id 查詢產品
        product = validated_data['product']
        quantity = validated_data['quantity']
        order_id = self.context.get('order_id')
        price = product.price

        # 嘗試查詢是否已經存在這個 order_item
        # 如果是創建，則使用這些初始值
        order_item, created = OrderItem.objects.get_or_create(
            order_id=order_id,
            product=product,
            defaults={'quantity': quantity, 'price': price}
        )

        # 如果已經存在，則只增加數量
        if not created:
            order_item.quantity += quantity
            order_item.save()

        return order_item


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'customer', 'status', 'placed_at',
                  'orderitem_set', 'total_price', 'shipping_address']
    orderitem_set = OrderItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()
    shipping_address = AddressSerializer()

    def get_total_price(self, order: Order):
        return sum([i.quantity*i.product.price for i in order.orderitem_set.all()])


class OrderCreateSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()
    shipping_address_id = serializers.IntegerField()

    def validate_cart_id(self, cart_id):
        if not Cart.objects.filter(pk=cart_id).exists():
            raise serializers.ValidationError('此 cart_id 不存在')
        if CartItem.objects.filter(cart_id=cart_id).count() == 0:
            raise serializers.ValidationError('無cartitem, 無法加入')
        return cart_id

    def save(self, **kwargs):
        with transaction.atomic():
            cart_id = self.validated_data['cart_id']
            shipping_address_id = self.validated_data['shipping_address_id']
            cartitem_set = CartItem.objects.select_related(
                'product').filter(cart_id=cart_id)
            order = Order.objects.create(
                customer_id=self.context['customer_id'],
                shipping_address_id=shipping_address_id
            )

            orderitem_set = [OrderItem(
                order=order,
                product=i.product,
                quantity=i.quantity,
                price=i.price
            ) for i in cartitem_set]

            OrderItem.objects.bulk_create(orderitem_set)

            Cart.objects.filter(pk=cart_id).delete()

            return order
