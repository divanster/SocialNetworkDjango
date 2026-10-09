import json

from django.test import TestCase
from django.urls import reverse


class GraphQLEndpointTests(TestCase):
    def test_get_graphql_without_query_is_non_500(self):
        response = self.client.get(reverse('graphql'))
        self.assertIn(response.status_code, (400, 405))

    def test_post_valid_query_works(self):
        response = self.client.post(
            reverse('graphql'),
            data=json.dumps({'query': '{ __typename }'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['data']['__typename'], 'Query')

    def test_post_invalid_query_returns_graphql_error(self):
        response = self.client.post(
            reverse('graphql'),
            data=json.dumps({'query': '{ invalidField }'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        payload = response.json()
        self.assertIn('errors', payload)
        self.assertTrue(payload['errors'])
