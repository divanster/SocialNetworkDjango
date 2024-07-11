from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
# Assuming you have a LikeViewSet in your views.py
router.register(r'likes', views.LikeViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
