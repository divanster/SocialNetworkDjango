from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
# Assuming you have a MessageViewSet in your views.py
router.register(r'messages', views.MessageViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
