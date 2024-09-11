from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (SpectacularAPIView, SpectacularRedocView,
                                   SpectacularSwaggerView)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, \
    TokenBlacklistView
from django.views.generic import RedirectView
from users.views import CustomUserSignupView


# Define the trigger_error view function
def trigger_error(request):
    division_by_zero = 1 / 0


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/signup/', CustomUserSignupView.as_view(), name='user-signup'),
    path('api/comments/', include('comments.urls')),
    path('api/follows/', include('follows.urls')),
    path('api/reactions/', include('reactions.urls')),
    path('api/messenger/', include('messenger.urls')),
    path('api/social/', include('social.urls')),
    path('api/users/', include('users.urls')),
    path('api/notifications/', include('notifications.urls')),
    path('api/albums/', include('albums.urls')),
    path('api/friends/', include('friends.urls')),
    path('api/newsfeed/', include('newsfeed.urls')),
    path('api/pages/', include('pages.urls')),
    path('api/stories/', include('stories.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'),
         name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'),
         name='redoc'),
    path('api/docs/', RedirectView.as_view(url='/api/schema/swagger-ui/',
                                           permanent=True)),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),
    path('sentry-debug/', trigger_error),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
                      path('__debug__/', include(debug_toolbar.urls)),
                  ] + urlpatterns
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
