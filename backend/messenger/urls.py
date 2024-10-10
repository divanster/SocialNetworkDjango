# backend/messenger/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MessageViewSet, MessagesCountView

app_name = 'messenger'

router = DefaultRouter()
router.register(r'', MessageViewSet, basename='message')

urlpatterns = [
    path('count/', MessagesCountView.as_view(), name='messages-count'),
    path('', include(router.urls)),
]
