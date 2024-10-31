from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NotificationViewSet, NotificationsCountView

app_name = 'notifications'

router = DefaultRouter()
router.register(r'notifications', NotificationViewSet, basename='notification')

urlpatterns = [
    path('notifications/count/', NotificationsCountView.as_view(), name='notifications-count'),
    path('', include(router.urls)),
]
