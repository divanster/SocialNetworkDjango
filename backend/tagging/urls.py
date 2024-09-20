# backend/tagging/urls.py
from rest_framework.routers import DefaultRouter
from .views import TaggedItemViewSet

router = DefaultRouter()
router.register(r'user-tags', TaggedItemViewSet, basename='user-tags')
urlpatterns = router.urls
