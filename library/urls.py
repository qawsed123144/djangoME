from rest_framework_nested import routers
from django.urls import path
from . import views

router = routers.DefaultRouter()

urlpatterns = router.urls + [
    path('esearch/', views.ArticleESView.as_view()),
    path('esearch/<str:id>/', views.ArticleDetailView.as_view()),
]
