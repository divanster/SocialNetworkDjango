# backend/graphql_validation.py

from graphql.validation import ValidationRule
from graphql.error import GraphQLError
from django.conf import settings


class ComplexityLimitRule(ValidationRule):
    def __init__(self, context):
        super().__init__(context)
        self.max_complexity = getattr(settings, 'GRAPHQL_MAX_COMPLEXITY', 100)  # Define your maximum allowed complexity
        self.current_complexity = 0
        self.complexity_map = {
            'user': 2,
            'posts': 5,
            'comments': 3,
            # Add more fields as necessary
        }

    def enter_field(self, node, *args):
        field_name = node.name.value
        complexity = self.complexity_map.get(field_name, 1)  # Default complexity is 1
        self.current_complexity += complexity
        if self.current_complexity > self.max_complexity:
            self.context.report_error(
                GraphQLError(
                    f"Query is too complex: {self.current_complexity}. Maximum allowed complexity is {self.max_complexity}.",
                    node
                )
            )

    def leave_field(self, node, *args):
        field_name = node.name.value
        complexity = self.complexity_map.get(field_name, 1)
        self.current_complexity -= complexity

    def enter_operation_definition(self, node, *args):
        self.current_complexity = 0


class DepthLimitRule(ValidationRule):
    def __init__(self, context):
        super().__init__(context)
        self.max_depth = getattr(settings, 'GRAPHQL_MAX_DEPTH', 10)  # Set your desired maximum depth here
        self.current_depth = 0
        self.max_reached = 0

    def enter_field(self, node, *args):
        self.current_depth += 1
        if self.current_depth > self.max_depth:
            self.context.report_error(
                GraphQLError(
                    f"Query is too deep: {self.current_depth}. Maximum allowed depth is {self.max_depth}.",
                    node
                )
            )
        self.max_reached = max(self.max_reached, self.current_depth)

    def leave_field(self, node, *args):
        self.current_depth -= 1

    def enter_operation_definition(self, node, *args):
        self.current_depth = 0
        self.max_reached = 0
