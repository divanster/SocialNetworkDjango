# backend/messages/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MessageViewSet, MessagesCountView

app_name = 'messages'

router = DefaultRouter()
router.register(r'', MessageViewSet, basename='message')  # Register at root

urlpatterns = [
    path('count/', MessagesCountView.as_view(), name='messages-count'),
    path('inbox/', MessageViewSet.as_view({'get': 'inbox'}), name='messages-inbox'),  # Define 'inbox' endpoint
    path('', include(router.urls)),
]
