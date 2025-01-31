# backend/notifications/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NotificationViewSet, NotificationsCountView

app_name = 'notifications'

router = DefaultRouter()
router.register(r'', NotificationViewSet, basename='notification')  # Register at root

urlpatterns = [
    path('count/', NotificationsCountView.as_view(), name='notifications-count'),
    path('', include(router.urls)),
]
