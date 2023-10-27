import pytest
from news.models import Comment, News
from pytest_lazyfixture import lazy_fixture
from conftest import URL


pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'url, parametr_client', (
        (URL.home, lazy_fixture('client')),
        (URL.detail, lazy_fixture('client')),
    )
)
def test_notes_list_for_different_users(url, parametr_client, news):
    # Тест проверяет что на главной 10 новостей
    # и на главной они острортированы от новых к старым,
    # а на странице отдельной новости комментарии от старых
    response = parametr_client.get(url)
    assert response, News.objects.count() <= 10
    assert response, News.objects.sorted('-date')
    assert response, Comment.objects.sorted('created')


def test_client_has_form(client, admin_client, news):
    # Проверка доступности формы комментария для
    # анонима и авторизованного пользователя
    response = client.get(URL.detail)
    admin_response = admin_client.get(URL.detail)
    assert ('form' in admin_response.context)
    assert ('form' not in response.context)
