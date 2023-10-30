import pytest
from collections import namedtuple
from django.conf import settings
from django.urls import reverse
from news.models import News, Comment
from datetime import datetime, timedelta


PK = 1

URL_NAME = namedtuple(
    'NAME',
    [
        'home',
        'detail',
        'edit',
        'delete',
        'login',
        'logout',
        'signup',
    ],
)

URL = URL_NAME(
    reverse('news:home'),
    reverse('news:detail', args=(PK,)),
    reverse('news:edit', args=(PK,)),
    reverse('news:delete', args=(PK,)),
    reverse('users:login'),
    reverse('users:logout'),
    reverse('users:signup'),
)


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def news():
    return News.objects.create(
        title='Заголовок',
        text='Текст заметки',
    )


@pytest.fixture
def news_count():
    today = datetime.today()
    news_count_on_page = News.objects.bulk_create(
        News(title=f'Новость {index}',
             text='Просто текст.',
             date=today - timedelta(days=index),
             )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )
    return news_count_on_page


@pytest.fixture
def comment_sorted_on_page(author, news):
    today = datetime.today()
    comment_sorted = Comment.objects.bulk_create(
        Comment(news=news,
                author=author,
                text='Текст комментария',
                created=today - timedelta(days=index),
                )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )
    return comment_sorted


@pytest.fixture
def url_detail_news(news):
    return reverse('news:detail', args=(news.pk,))


@pytest.fixture
def redirect_url_detail_news(users_login_url, comment):
    next_url = reverse('news:detail', args=(comment.pk,))
    return f"{users_login_url}?next={next_url}"


@pytest.mark.django_db
def comment(news, author):
    return Comment.objects.create(
        news=news,
        author=author,
        text='Новый коммент',
    )


@pytest.fixture
def id_for_args(news):
    return (news.id,)


@pytest.fixture
def form_data():
    return {
        'text': 'Новый текст',
    }


@pytest.fixture
def comment(author, news):
    return Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария',
    )
