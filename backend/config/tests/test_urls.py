# backend/config/tests/test_urls.py

from django.test import SimpleTestCase
from django.urls import reverse, resolve
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, \
    SpectacularRedocView
from core.views import health_check, csp_report


class URLTests(SimpleTestCase):

    def test_health_check_url_resolves(self):
        """
        Test that the health check URL resolves correctly.
        """
        url = reverse('health_check')
        self.assertEqual(resolve(url).func, health_check)

    def test_csp_report_url_resolves(self):
        """
        Test that the CSP report URL resolves correctly.
        """
        url = reverse('csp_report')
        self.assertEqual(resolve(url).func, csp_report)

    def test_swagger_ui_url_resolves(self):
        """
        Test that the Swagger UI URL resolves correctly.
        """
        url = reverse('swagger-ui')
        self.assertEqual(resolve(url).func.view_class, SpectacularSwaggerView)

    def test_redoc_url_resolves(self):
        """
        Test that the ReDoc URL resolves correctly.
        """
        url = reverse('redoc')
        self.assertEqual(resolve(url).func.view_class, SpectacularRedocView)

    def test_schema_url_resolves(self):
        """
        Test that the Schema URL resolves correctly.
        """
        url = reverse('schema')
        self.assertEqual(resolve(url).func.view_class, SpectacularAPIView)
