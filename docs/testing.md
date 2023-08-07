# Test Strategy

Shepherd's test code is in the `consvc_shepherd/tests` directory.

## Unit Tests

The unit layer is suitable for testing complex behavior at a small scale, 
with fine-grained control over the inputs. 
Due to their narrow scope, unit tests are fundamental to thorough test coverage.

Our test coverage minimum is set to 95%. 
A coverage report is printed to the shell showing the test results and possible exceptions.

Unit tests are written and executed with `pytest` and are located in the `consvc_shepherd/tests/`
directory. The name of individual test files should match those of the files they are testing.
Ex. `models.py` should be `test_models.py`. 

To execute unit tests, use: `make test`. By default, these tests run in CI during each push 
to an active PR and during the merge process.

## Testing a Django App

Django provides a number of tools, API methods, and classes to test web and Django-specific behavior.
These allow you to simulate requests, insert test data, and inspect your application's output.
See the most recent [Django test docs][django-test-docs] for reference.

To write a test, import the `TestCase` base class from`django.test` and pass it to your test class.
This creates a clean database before tests are run and each test function is run in its own transaction.
You can also use the `Client` from `django.test` to simulate user interactions at the view level.
Any test class created should generally inherit from `TestCase`.

Common set up and tear down methods are defined (as shown below), allowing you to pre-define forms,
models and data for testing.

For example:
```python
from django.test import TestCase

class MyTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up data for the whole TestCase
        cls.foo = Foo.objects.create(bar="Test")
        ...
    
    def setUp(self):
        # Setup run before every test method.
        pass

    def tearDown(self):
        # Clean up run after every test method.
        pass

    def test1(self):
        # Some test using self.foo
        ...

    def test2(self):
        # Some other test using self.foo
        ...

```

[django-test-docs]: https://docs.djangoproject.com/en/4.2/topics/testing/tools/