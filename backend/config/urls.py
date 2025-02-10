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

from core.graphql_views import CustomGraphQLView
from schema import schema

urlpatterns = [
    # Admin and health endpoints
    path('admin/', admin.site.urls),
    path('health/', health_check, name='health_check'),
    path('csp-violation-report/', csp_report, name='csp_report'),

    # Homepage with a welcome message
    path('', lambda request: HttpResponse("Welcome to the Social Network API!"), name='home'),

    # Add the GraphQL endpoint here
    path('graphql/', CustomGraphQLView.as_view(graphiql=True, schema=schema), name='graphql'),
    # path('graphql/', CustomGraphQLView.as_view(graphiql=settings.DEBUG,
    # schema=schema), name='graphql'), path('graphql/', CustomGraphQLView.as_view(
    # graphiql=True)),


    # API Versioning - Versioned API URLs
    path('api/v1/', include([
        # JWT Authentication endpoints
        path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
        path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
        path('token/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),

        # Include app-specific URLs with namespaces for versioning
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
        path('stories/', include(('stories.urls', 'stories'), namespace='stories')),
    ])),
]

# API Schema and Documentation URLs
urlpatterns += [
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('api/docs/', RedirectView.as_view(url='/api/schema/swagger-ui/', permanent=True)),
]
# # Custom error handlers for handling specific HTTP errors
# handler400 = 'config.views.custom_400_view'
# handler403 = 'config.views.custom_403_view'
# handler404 = 'config.views.custom_404_view'
# handler500 = 'config.views.custom_500_view'

# Serving static and media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
