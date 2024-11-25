# backend/graphql_views.py

from graphene_django.views import GraphQLView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed
from django.http import JsonResponse
from django.contrib.auth.models import AnonymousUser


class CustomGraphQLView(GraphQLView):
    """
    Custom GraphQL view to handle JWT authentication for GraphQL queries.
    """

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def parse_body(self, request):
        """
        Attempt to authenticate the request using JWT tokens.
        If token is present and valid, set the user in the request context.
        """
        auth = JWTAuthentication()
        try:
            user_auth_tuple = auth.authenticate(request)
            if user_auth_tuple is not None:
                request.user, request.token = user_auth_tuple
            else:
                request.user = AnonymousUser()
        except (InvalidToken, AuthenticationFailed):
            request.user = AnonymousUser()

        return super().parse_body(request)
