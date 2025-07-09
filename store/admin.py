from django.contrib import admin
from django import forms
from . import models

admin.site.register(models.Collection)


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'price', 'inventory_status', 'collection']
    list_editable = ['price']
    list_per_page = 20

    @admin.display(ordering='inventory')
    def inventory_status(self, product):
        if product.inventory < 10:
            return 'LOW'
        return 'OK'


class AddressInline(admin.TabularInline):
    model = models.Address
    extra = 1


@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'membership']
    list_editable = ['membership']
    inlines = [AddressInline]
    ordering = ['first_name', 'last_name']
    list_filter = ['membership']
    search_fields = ['first_name__istartswith', 'last_name__istartswith']
    list_per_page = 20


class CartItemInline(admin.TabularInline):
    model = models.CartItem
    extra = 0


@admin.register(models.Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'create_date']
    inlines = [CartItemInline]
    list_per_page = 20


class OrderItemInline(admin.TabularInline):
    model = models.OrderItem
    extra = 1


class OrderForm(forms.ModelForm):
    class Meta:
        model = models.Order
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        customer = self.instance.customer
        if customer:
            self.fields['shipping_address'].queryset = models.Address.objects.filter(customer=customer)
        else:
            self.fields['shipping_address'].queryset = models.Address.objects.none()

@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    form = OrderForm
    list_display = ['id', 'placed_at', 'customer', 'shipping_address']
    inlines = [OrderItemInline]
    list_per_page = 20
