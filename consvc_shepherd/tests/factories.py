"""Factory test module for consvc_shepherd."""

import factory
from django.contrib.auth import get_user_model
from faker import Factory as FakerFactory

faker = FakerFactory.create()


class UserFactory(factory.django.DjangoModelFactory):
    """UserFactor class containing mock data for user.

    Attributes
    ----------
    first_name : str
        user first name
    last_name : str
        user last name
    email : str
        user email
    username : str
        username
    """

    first_name = factory.LazyAttribute(lambda o: faker.first_name())  # type: ignore [attr-defined]
    last_name = factory.LazyAttribute(lambda o: faker.last_name())  # type: ignore [attr-defined]
    email = factory.LazyAttribute(lambda o: faker.company_email())  # type: ignore [attr-defined]
    username = factory.LazyAttribute(lambda o: o.email)

    class Meta:
        """Meta class to bind model to get_user_model()."""

        model = get_user_model()
