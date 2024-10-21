"""Unit tests for all the database views"""

import json
import os

from django.db import connection
from django.test import TestCase


class ViewColumnTest(TestCase):
    """Unit tests for each view. The views and required columns are defined externally.
    This allows us to easily see diffs when addinig, editing, or removing test cases
    """

    def assert_view_columns(self, view_name, required_columns):
        """Iterate over each view to assert that the view has the required columns."""
        with connection.cursor() as cursor:
            try:
                actual_columns = {
                    col.name
                    for col in connection.introspection.get_table_description(
                        cursor, view_name
                    )
                }
            except Exception as e:
                self.fail(f"Failed to get view description for '{view_name}': {e}")

        missing_columns = required_columns - actual_columns
        extra_columns = actual_columns - required_columns

        error_message = f"Column mismatch in view '{view_name}':\n"
        error_message += (
            f"  Missing columns: {', '.join(sorted(missing_columns)) or 'None'}\n"
        )
        error_message += (
            f"  Unexpected columns: {', '.join(sorted(extra_columns)) or 'None'}"
        )

        # Assert that the actual columns match the required columns
        self.assertSetEqual(actual_columns, required_columns, error_message)

    def test_views_have_required_columns(self):
        """Test multiple database views to ensure they have the required columns.
        The view names and columns are defined in view_definitions.json
        """
        base_dir = os.path.dirname(os.path.abspath(__file__))
        view_definitions_file = os.path.join(base_dir, "view_definitions.json")
        views_to_test = None
        with open(view_definitions_file) as view_definition:
            views_to_test_json = json.load(view_definition)
            views_to_test = [
                (view_info["view_name"], set(view_info["required_columns"]))
                for view_info in views_to_test_json
            ]

        for view_name, required_columns in views_to_test:
            with self.subTest(view=view_name):
                self.assert_view_columns(view_name, required_columns)
