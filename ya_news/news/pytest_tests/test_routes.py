import pytest
from http import HTTPStatus

from pytest_django.asserts import assertRedirects
from pytest_lazyfixture import lazy_fixture

from conftest import URL


pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'url, parametrized_client, expected_status', (
        (URL.home, lazy_fixture('client'), HTTPStatus.OK),
        (URL.detail, lazy_fixture('client'), HTTPStatus.OK),
        (URL.login, lazy_fixture('client'), HTTPStatus.OK),
        (URL.logout, lazy_fixture('client'), HTTPStatus.OK),
        (URL.signup, lazy_fixture('client'), HTTPStatus.OK),
        (URL.edit, lazy_fixture('author_client'), HTTPStatus.OK),
        (URL.delete, lazy_fixture('author_client'), HTTPStatus.OK),
        (URL.edit, lazy_fixture('admin_client'), HTTPStatus.NOT_FOUND),
        (URL.delete, lazy_fixture('admin_client'), HTTPStatus.NOT_FOUND),
    ),
)
def test_pages_accessibility(
        url, parametrized_client, expected_status, comment):
    """Проверка доступа к страницам."""
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url',
    (URL.edit, URL.delete),
)
def test_redirects(client, url, comment):
    """Проверка редиректа для анонима."""
    expected_url = f'{URL.login}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
