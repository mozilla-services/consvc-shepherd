# Test Strategy

Shepherd's test code is in the `consvc_shepherd/tests` directory.

## Unit Tests

The unit layer is suitable for testing complex behavior at a small scale, 
with fine-grained control over the inputs. 
Due to their narrow scope, unit tests are fundamental to thorough test coverage.

Our test coverage minimum is set to 95%. 
A coverage report is printed to the shell showing the test results and possible exceptions. See [coverage.py](https://coverage.readthedocs.io/en/latest/) for more details.

Unit tests are written and executed with `pytest` and are located in the `consvc_shepherd/tests/`
directory. The name of individual test files should match those of the files they are testing in the form `test*.py`.
Ex. `models.py` should be `test_models.py`. 

To execute unit tests, use: `make test`. By default, these tests run in CI during each push 
to an active PR and during the merge process.

## Testing a Django App

Django provides a number of tools, API methods, and classes to test web and Django-specific behavior.
These allow you to simulate requests, insert test data, and inspect your application's output.
See the most recent [Django test docs][django-test-docs] for reference.

To write a test, import the `TestCase` base class from `django.test` and pass it to your test class. 
This creates a clean database before tests are run and each test function is run in its own transaction. 

You can also use the `Client` from `django.test` to simulate user interactions at the view level.
Any test class created should generally inherit from `TestCase`, 
though you can check the Django test documentation for other test classes. `SimpleTestCase` can also be used in instances where tests don't use the database or test client.

Define all your test methods within an individual class, based on the functionality you are testing. Common set up and tear down methods are defined (as shown below), allowing you to pre-define forms,
models and data for testing.

`setUpTestData()` is called once at the beginning of the test run for class-level setup. You'd use this to create objects that aren't going to be modified or changed in any of the test methods.

`setUp()` is called before every test function to set up any objects that may be modified by the test (every test function will get a "fresh" version of these objects).

For example:
```python
from django.test import TestCase

class MyTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up data for the whole TestCase
        # setUpTestData: Run once to set up non-modified data for all class methods.
        cls.foo = Foo.objects.create(bar="Test")
        ...
    
    def setUp(self):
        # Setup run before every test method.
        # setUp: Run once for every test method to setup clean data.
        pass

    def tearDown(self):
        # Clean up run after every test method.
        # tearDown: Run once for every test method to clean data after run.
        pass

    def test1(self):
        # Some test using self.foo
        ...

    def test2(self):
        # Some other test using self.foo
        ...

```

### Test Models

To ensure models properly validate data passed to them, explicitly testing for fields and labels is a best practice.

Create the models you wish to test using `objects.create` and run assertions against the model and expected behavior.

Example:
```python
class FooModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        Foo.objects.create(first='foo', last='bar')

    def test_name_label(self):
        foo = Foo.objects.get(id=1)
        field_label = foo._meta.get_field('first').verbose_name
        self.assertEqual(field_label, 'first')
```
### Test Forms

When testing forms, it's generally sufficient to ensure that the forms have the desired fields, along with any custom logic related to their validation.

Create an instance of your form to test. Form fields of type `forms.Form` can be accessed via `form.fields["field_name"]`.

### Test Views

Use the Django test `Client` to validate view behavior, which simulates `GET` and `POST` requests to observe and validate responses. 
The `Client` belongs to `TestCase`'s derived class, therefore you can do the following:

```python
response = self.client.get('/url/to/resource/')
```
`response.context` is the context variable passed to the template by the view, which generally contains the most valuable information when testing.

[django-test-docs]: https://docs.djangoproject.com/en/4.2/topics/testing/tools/