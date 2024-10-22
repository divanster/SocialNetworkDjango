# backend/config/tests/test_error_views.py

from django.test import TestCase, Client
from django.urls import re_path
from django.http import HttpResponse, HttpResponseForbidden, Http404
from django.shortcuts import render
from config.views import custom_400_view, custom_403_view, custom_404_view, \
    custom_500_view


# Mock views to trigger specific errors for testing purposes
def bad_request_view(request):
    return custom_400_view(request)


def protected_view(request):
    return HttpResponseForbidden('Permission Denied')


def raise_not_found(request):
    raise Http404('Not Found')


def raise_server_error(request):
    raise Exception('Server Error')


# Include temporary URLs for testing custom error views
urlpatterns = [
    re_path(r'^bad-request/$', bad_request_view),
    re_path(r'^some_protected_view/$', protected_view),
    re_path(r'^raise-server-error/$', raise_server_error),
    re_path(r'^non-existing-url/$', raise_not_found),  # Non-existent URL for 404
]


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
        self.assertContains(response, "The requested resource was not found",
                            status_code=404)

    def test_custom_500_view(self):
        response = self.client.get('/raise-server-error/', follow=True)
        self.assertEqual(response.status_code, 500)
        self.assertContains(response, "An internal server error occurred",
                            status_code=500)
