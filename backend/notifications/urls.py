from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NotificationViewSet, NotificationsCountView

router = DefaultRouter()
router.register(r'notifications', NotificationViewSet)

urlpatterns = [
    path('notifications/count/', NotificationsCountView.as_view(), name='notifications-count'),
    path('', include(router.urls)),
]
