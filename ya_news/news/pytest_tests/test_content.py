import pytest
from django.conf import settings

from conftest import URL
from news.forms import CommentForm

pytestmark = pytest.mark.django_db


def test_news_count_on_main(client, news_count):
    """Проверка количества новостей на главной."""
    response = client.get(URL.home)
    assert 'object_list' in response.context
    news_list = list(response.context['object_list'])
    assert len(news_list) == settings.NEWS_COUNT_ON_HOME_PAGE


def test_comment_sorted_on_main(client, comment_sorted_on_page):
    """Проверка сортировки комментариев на главной."""
    response = client.get(URL.home)
    assert 'object_list' in response.context
    object_list = response.context['object_list']
    all_dates = [comment.date for comment in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_news_sorted_on_main(client, news_count):
    """Проверка сортировки новостей на главной."""
    response = client.get(URL.home)
    assert 'object_list' in response.context
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_client_has_form(client, news):
    """Проверка доступности формы комментария для
    авторизованного пользователя.
    """
    response = client.get(URL.detail)
    assert ('form' not in response.context)


def test_anonymous_has_form(admin_client, news):
    """Проверка доступности формы комментария для анонима."""
    admin_response = admin_client.get(URL.detail)
    assert ('form' in admin_response.context)


@pytest.mark.parametrize('client_type', ['client', 'admin_client'])
def test_comment_form_access(client_type, client, admin_client, news):
    response = client.get(URL.detail)
    if client_type == 'client':
        assert 'form' not in response.context
    else:
        response = admin_client.get(URL.detail)
        assert isinstance(response.context['form'], CommentForm)
        assert 'form' in response.context
