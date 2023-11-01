from django.conf import settings

import pytest

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


@pytest.mark.parametrize(
    ('client_type', 'forms'),
    [(pytest.lazy_fixture('client'), False),
     (pytest.lazy_fixture('admin_client'), True)
     ])
def test_comment_form_access(client_type, forms, client, admin_client, news):
    response = client_type.get(URL.detail)
    if forms is True:
        assert isinstance(
            response.context['form'], CommentForm
        )
    assert ('form' in response.context) is forms
