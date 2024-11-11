# backend/config/tests/test_views.py

from django.test import TestCase, Client, override_settings
from django.urls import path
from django.http import Http404
from config.views import custom_400_view, custom_403_view, custom_404_view, custom_500_view

# Mock views to trigger specific errors for testing purposes
def bad_request_view(request):
    return custom_400_view(request)

def protected_view(request):
    return custom_403_view(request)

def raise_not_found(request):
    raise Http404('Not Found')

def raise_server_error(request):
    raise Exception('Server Error')

# Define a separate URL configuration for testing purposes
urlpatterns = [
    path('bad-request/', bad_request_view),
    path('some_protected_view/', protected_view),
    path('non-existing-url/', raise_not_found),
    path('raise-server-error/', raise_server_error),
]

@override_settings(ROOT_URLCONF='config.tests.test_views')
class ConfigAppViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()

    def test_custom_400_view(self):
        response = self.client.get('/bad-request/')
        self.assertEqual(response.status_code, 400)
        self.assertContains(response, "Invalid request", status_code=400)

    def test_custom_403_view(self):
        response = self.client.get('/some_protected_view/')
        self.assertEqual(response.status_code, 403)
        self.assertContains(response, "Permission Denied", status_code=403)

    def test_custom_404_view(self):
        response = self.client.get('/non-existing-url/')
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "The requested resource was not found", status_code=404)

    def test_custom_500_view(self):
        response = self.client.get('/raise-server-error/', follow=True)
        self.assertEqual(response.status_code, 500)
        self.assertContains(response, "An unexpected error occurred.", status_code=500)
