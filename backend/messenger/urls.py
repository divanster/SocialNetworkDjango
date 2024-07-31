from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MessageViewSet, MessagesCountView

router = DefaultRouter()
router.register(r'messages', MessageViewSet)

urlpatterns = [
    path('messages/count/', MessagesCountView.as_view(), name='messages-count'),
    path('', include(router.urls)),
]
