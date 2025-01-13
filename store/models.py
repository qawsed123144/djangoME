from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, AbstractUser
from django.core.validators import MinValueValidator
from uuid import uuid4

# 更改系統的 createuser


class CustomerManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("必須提供電子郵件")
        email = self.normalize_email(email)
        extra_fields.setdefault("is_active", True)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if not extra_fields.get("is_staff"):
            raise ValueError("管理員必須設置 is_staff=True")
        if not extra_fields.get("is_superuser"):
            raise ValueError("管理員必須設置 is_superuser=True")

        return self.create_user(email, password, **extra_fields)


class Customer(AbstractBaseUser, PermissionsMixin):
    MEMBERSHIP_CHOICES = [
        ("G", "GOLD"),
        ("S", "SILVER"),
        ("B", "BRONZE"),
    ]
###########
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    birth_date = models.DateField(null=True)
    membership = models.CharField(
        max_length=1, choices=MEMBERSHIP_CHOICES, default="B"
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
############
    objects = CustomerManager()  # 更改系統的 createuser
    USERNAME_FIELD = "email"  # 使用 email 進行身份識別
    REQUIRED_FIELDS = ["first_name", "last_name"]
###########

    class Meta:
        ordering = ["first_name"]

    def __str__(self):
        return self.email


class Address(models.Model):
    # ForeignKey(1->1)
    customer = models.OneToOneField(
        Customer, primary_key=True, on_delete=models.CASCADE)
    zip = models.IntegerField(null=True)
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)


class Collection(models.Model):
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['title']


class Product(models.Model):
    # ForeignKey(1->many)
    collection = models.ForeignKey(
        Collection, on_delete=models.PROTECT)
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.IntegerField()
    inventory = models.IntegerField()
    update_date = models.DateField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['title']


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product/')


class Review(models.Model):
    # ForeignKey(1->many)
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='reviews')
    name = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateField(auto_now_add=True)


class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    create_date = models.DateField(auto_now=True)


class CartItem(models.Model):
    # ForeignKey(1->many)
    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE)
    # ForeignKey(1->many)
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)]
    )
    price = models.IntegerField()

    class Meta:
        unique_together = [['cart', 'product']]


class Order(models.Model):
    status = [
        ('P', 'Pending'),
        ('C', 'Complete'),
        ('F', 'Failed')]
    # ForeignKey(1->many)
    customer = models.ForeignKey(
        Customer, on_delete=models.PROTECT)
    status = models.CharField(max_length=1, choices=status, default='P')
    placed_at = models.DateField(auto_now=True)


class OrderItem(models.Model):
    # ForeignKey(1->many)
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE)
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField()
    price = models.IntegerField()
