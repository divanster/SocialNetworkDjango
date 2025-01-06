# backend/config/validation.py

from graphql.validation import ValidationRule
from graphql.error import GraphQLError


class DepthLimitRule(ValidationRule):
    def __init__(self, context):
        super().__init__(context)
        self.max_depth = 10  # Set your desired maximum depth here
        self.current_depth = 0

    def enter_field(self, node, *args):
        self.current_depth += 1
        if self.current_depth > self.max_depth:
            self.context.report_error(
                GraphQLError(
                    f"Query is too deep: {self.current_depth}. Maximum allowed depth is {self.max_depth}.",
                    node
                )
            )

    def leave_field(self, node, *args):
        self.current_depth -= 1

    # Reset depth when entering a new operation
    def enter_operation_definition(self, node, *args):
        self.current_depth = 0
