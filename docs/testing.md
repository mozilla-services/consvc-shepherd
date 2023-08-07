# Test Strategy

Shepherd's test code is in the `consvc_shepherd/tests` directory.

## Unit Tests

The unit layer is suitable for testing complex behavior at a small scale, 
with fine-grained control over the inputs. 
Due to their narrow scope, unit tests are fundamental to thorough test coverage.

Our test coverage minimum is set to 95%. 
A coverage report is printed to the shell showing the test results and possible exceptions.

To execute unit tests, use: `make test`

Unit tests are written and executed with pytest and are located in the `consvc_shepherd/tests`
directory.

Django provides a number of tools, API methods, and classes to test web and Django-specific behavior.
These allow you to simulate requests, insert test data, and inspect your application's output.

All tests require you to import the `TestCase` base class from`django.test`.
Any test class created should inherit from `TestCase`.

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