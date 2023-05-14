from profiles.models import Profile


def test_profile_saved_on_user_creation(sample_user):
    assert sample_user.profile == Profile.objects.get(user=sample_user)


def test_profile_full_name_field(sample_user):
    assert sample_user.profile.full_name == "john doe"
