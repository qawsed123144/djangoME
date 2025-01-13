from rest_framework_nested import routers
from . import views

router = routers.DefaultRouter()
router.register('collections', views.CollectionViewSet)

router.register('products', views.ProductViewSet)
products_router = routers.NestedDefaultRouter(
    router, 'products', lookup='product')
products_router.register('images', views.ProductImageViewSet,
                         basename='product-images')
products_router.register('reviews', views.ReviewViewSet,
                         basename='product-reviews')

router.register('carts', views.CartViewSet)
carts_router = routers.NestedDefaultRouter(
    router, 'carts', lookup='cart')
carts_router.register('cartitem_set', views.CartItemViewSet,
                      basename='cart-cartitem_set')

router.register('orders', views.OrderViewSet, basename='orders')

urlpatterns = router.urls + products_router.urls + \
    carts_router.urls
