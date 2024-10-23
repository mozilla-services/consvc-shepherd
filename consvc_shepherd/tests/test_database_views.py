"""Unit tests for all the database views"""

from django.apps import apps
from django.db import connection
from django.test import TestCase


class ViewModelAlignmentTest(TestCase):
    """Unit tests for each view. The views are automatically detected using apps.get_models()
    and filtering for models that are not managed.
    """

    def assert_view_matches_model(self, model_class):
        """Assert that the database view associated with the given unmanaged model
        has columns that match the model's fields.
        """
        expected_columns = set(field.column for field in model_class._meta.fields)
        view_name = model_class._meta.db_table
        with connection.cursor() as cursor:
            try:
                actual_columns = {
                    col.name
                    for col in connection.introspection.get_table_description(
                        cursor, view_name
                    )
                }
            except Exception as e:
                self.fail(f"Failed to get view columns for '{view_name}': {e}")

        missing_columns = expected_columns - actual_columns
        extra_columns = actual_columns - expected_columns

        error_message = f"Column mismatch between model '{model_class.__name__}' and view '{view_name}':\n"
        error_message += f"  Missing columns in view: {', '.join(sorted(missing_columns)) or 'None'}\n"
        error_message += (
            f"  Extra columns in view: {', '.join(sorted(extra_columns)) or 'None'}"
        )

        self.assertSetEqual(actual_columns, expected_columns, error_message)

    def test_view_models_align_with_views(self):
        """Test that all unmanaged models representing database views have fields
        that match the columns in the database views.
        """
        unmanaged_models = [
            m
            for m in apps.get_models()
            if not m._meta.managed and not m._meta.abstract and not m._meta.proxy
        ]
        for model_class in unmanaged_models:
            with self.subTest(model=model_class.__name__):
                self.assert_view_matches_model(model_class)
