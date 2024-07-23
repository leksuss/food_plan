import pytest

from baseapp.models import CustomUser


@pytest.mark.django_db
def test_adding_user():
    user = CustomUser.objects.create_user(
        name='Boris',
        email='testemail.gmail.com',
        password='testpassword!!!!',
    )
    assert user.name == 'Boris'
    assert user.email == 'testemail.gmail.com'


@pytest.mark.django_db
def test_user_not_found():
    user = CustomUser.objects.create_user(
        name='Boris',
        email='testemail.gmail.com',
        password='testpassword!!!!',
    )
    id_user = user.id
    user.delete()

    with pytest.raises(CustomUser.DoesNotExist):
        CustomUser.objects.get(id=id_user)
