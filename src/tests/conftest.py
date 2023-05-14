import pytest
from profiles.models import Profile


@pytest.fixture
def msg():
    return {
        "email": "sam@tardy.com",
        "category": "Feedback",
        "message": "Hello World!",
    }


@pytest.fixture
def sample_user(django_user_model):
    user = django_user_model.objects.create(
        email="john@john.com",
        username="userjohn",
        first_name="john",
        last_name="doe",
        password="qwer1234qwer1234",
    )
    Profile.objects.create(user=user, first_name="john", last_name="doe")
    return user
