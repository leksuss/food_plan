import pytest

from baseapp.templatetags.baseapp_extras import ru_plural


@pytest.mark.parametrize('input, expected', [
    (1, 'рубль'),
    (2, 'рубля'),
    (5, 'рублей'),
    (11, 'рублей'),
    (14, 'рублей'),
    (21, 'рубль'),
    (24, 'рубля'),
])

def test_valid_email(input, expected):
    assert ru_plural(input, 'рубль,рубля,рублей') == expected
