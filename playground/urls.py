from django.urls import path
from . import views


urlpatterns = [
    path('', views.homepage, name="homepage"),
    path('cache-test/', views.cache_test),
]