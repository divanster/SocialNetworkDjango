# backend/tagging/urls.py
from rest_framework.routers import DefaultRouter
from .views import TaggedItemViewSet

router = DefaultRouter()
router.register(r'tagged-items', TaggedItemViewSet, basename='tagged-items')

urlpatterns = router.urls
