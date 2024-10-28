from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView, TokenRefreshView, TokenBlacklistView
)
from django.views.generic import RedirectView
from core.views import health_check, csp_report  # Import health_check and csp_report

urlpatterns = [
    # Non-API URLs
    path('admin/', admin.site.urls),
    path('health/', health_check, name='health_check'),  # Health check endpoint
    path('csp-violation-report/', csp_report, name='csp_report'),
    path('', lambda request: HttpResponse("Welcome to the Social Network API!"), name='home'),  # Homepage with a welcome message
]

# API Versioning - Versioned API URLs
api_v1_patterns = [
    # Include app-specific URLs with namespaces for versioning
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),
    path('comments/', include(('comments.urls', 'comments'), namespace='comments')),
    path('follows/', include(('follows.urls', 'follows'), namespace='follows')),
    path('reactions/', include(('reactions.urls', 'reactions'), namespace='reactions')),
    path('messenger/', include(('messenger.urls', 'messenger'), namespace='messenger')),
    path('social/', include(('social.urls', 'social'), namespace='social')),
    path('users/', include(('users.urls', 'users'), namespace='users')),
    path('notifications/', include(('notifications.urls', 'notifications'), namespace='notifications')),
    path('albums/', include(('albums.urls', 'albums'), namespace='albums')),
    path('tagging/', include(('tagging.urls', 'tagging'), namespace='tagging')),
    path('friends/', include(('friends.urls', 'friends'), namespace='friends')),
    path('newsfeed/', include(('newsfeed.urls', 'newsfeed'), namespace='newsfeed')),
    path('pages/', include(('pages.urls', 'pages'), namespace='pages')),
    path('stories/', include(('stories.urls', 'stories'), namespace='stories')),
]

# Including Swagger/OpenAPI schema endpoints
urlpatterns += [
    # API Schema URLs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('api/docs/', RedirectView.as_view(url='/api/schema/swagger-ui/', permanent=True)),

    # Include versioned API URLs under the prefix 'api/v1/'
    path('api/v1/', include((api_v1_patterns, 'api_v1'), namespace='api_v1')),
]

# # Custom error handlers for handling specific HTTP errors
# handler400 = 'config.views.custom_400_view'
# handler403 = 'config.views.custom_403_view'
# handler404 = 'config.views.custom_404_view'
# handler500 = 'config.views.custom_500_view'

# Add debug toolbar and static/media URLs for development if DEBUG is True
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) \
      + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
