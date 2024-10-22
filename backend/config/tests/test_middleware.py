# backend/config/tests/test_error_middleware.py

from django.test import TestCase, RequestFactory
from django.core.exceptions import PermissionDenied
from django.http import Http404
from config.custom_error_middleware import CustomErrorMiddleware


class CustomErrorMiddlewareTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = CustomErrorMiddleware(lambda req: None)

    def test_permission_denied_handled(self):
        """
        Test that PermissionDenied returns a 403 response.
        """
        request = self.factory.get('/')
        response = self.middleware.process_exception(request,
                                                     PermissionDenied("Access Denied"))
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['error']['type'], 'PermissionDenied')

    def test_http_404_handled(self):
        """
        Test that Http404 returns a 404 response.
        """
        request = self.factory.get('/')
        response = self.middleware.process_exception(request, Http404("Not Found"))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['error']['type'], 'NotFound')

    def test_unhandled_exception_handled(self):
        """
        Test that an unhandled exception returns a 500 response.
        """
        request = self.factory.get('/')
        response = self.middleware.process_exception(request, Exception("Server error"))
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json()['error']['type'], 'ServerError')
