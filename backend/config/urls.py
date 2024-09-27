from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (SpectacularAPIView, SpectacularRedocView,
                                   SpectacularSwaggerView)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView,
)
from django.views.generic import RedirectView
from users.views import CustomUserSignupView
from core.views import health_check, csp_report  # Import health_check

urlpatterns = [
    # Non-API URLs
    path('admin/', admin.site.urls),
    path('health/', health_check, name='health_check'),  # Health check endpoint
    path('csp-violation-report/', csp_report, name='csp_report'),

    # API URLs
    # Remove the redundant 'api/auth/signup/' path to avoid conflicts
    # path('api/auth/signup/', CustomUserSignupView.as_view(), name='user-signup'),

    path('api/comments/', include(('comments.urls', 'comments'), namespace='comments')),
    path('api/follows/', include(('follows.urls', 'follows'), namespace='follows')),
    path('api/reactions/', include(('reactions.urls', 'reactions'), namespace='reactions')),
    path('api/messenger/', include(('messenger.urls', 'messenger'), namespace='messenger')),
    path('api/social/', include(('social.urls', 'social'), namespace='social')),
    path('api/users/', include(('users.urls', 'users'), namespace='users')),
    path('api/notifications/', include(('notifications.urls', 'notifications'), namespace='notifications')),
    path('api/albums/', include(('albums.urls', 'albums'), namespace='albums')),
    path('api/tagging/', include(('tagging.urls', 'tagging'), namespace='tagging')),
    path('api/friends/', include(('friends.urls', 'friends'), namespace='friends')),
    path('api/newsfeed/', include(('newsfeed.urls', 'newsfeed'), namespace='newsfeed')),
    path('api/pages/', include(('pages.urls', 'pages'), namespace='pages')),
    path('api/stories/', include(('stories.urls', 'stories'), namespace='stories')),

    # Swagger and API schema documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'),
         name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'),
         name='redoc'),
    path('api/docs/', RedirectView.as_view(url='/api/schema/swagger-ui/',
                                           permanent=True)),

    # JWT Token endpoints
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),
]

# Add debug toolbar and static/media URLs for development
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) \
      + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
