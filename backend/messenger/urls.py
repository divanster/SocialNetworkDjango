from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MessageViewSet, MessagesCountView

app_name = 'messages'

router = DefaultRouter()
router.register(r'messages', MessageViewSet, basename='message')

urlpatterns = [
    path('messages/count/', MessagesCountView.as_view(), name='messages-count'),
    path('', include(router.urls)),
]
