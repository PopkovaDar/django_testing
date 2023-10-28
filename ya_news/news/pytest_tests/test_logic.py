import pytest
from http import HTTPStatus

from pytest_django.asserts import assertRedirects, assertFormError
from news.forms import WARNING, BAD_WORDS
from conftest import URL

from news.models import Comment


pytestmark = pytest.mark.django_db


def test_user_can_create_comment(author_client, author, news, form_data):
    """Проверка создания комментария авторизованным пользователем."""
    response = author_client.post(URL.detail, data=form_data)
    new_comment_count = Comment.objects.count()
    new_comment = Comment.objects.get()
    assertRedirects(response, f'{URL.detail}#comments')
    assert Comment.objects.count() == new_comment_count
    assert new_comment.text == form_data['text']
    assert new_comment.author == author
    assert new_comment.news == news


def test_anonymous_user_cant_create_comment(client, news, form_data):
    """Проверка создания комментария анонимом."""
    comment_count = Comment.objects.count()
    client.post(URL.detail, data=form_data)
    new_comment_count = Comment.objects.count()
    assert comment_count == new_comment_count


@pytest.mark.parametrize('word', BAD_WORDS)
def test_user_cant_create_comment_bad_words(author_client, news, word):
    """Проверка возможности отправки коммента с запрещенными словами."""
    before_comment_count = Comment.objects.count()
    bad_new_comment = {'text': f'{word} и тд.'}
    response = author_client.post(URL.detail, data=bad_new_comment)
    after_comment_count = Comment.objects.count()
    assertFormError(response, form='form', field='text', errors=WARNING)
    assert before_comment_count == after_comment_count


def test_author_can_edit_comment(author_client, form_data, news, comment):
    """Проверка редактирования комментария автором."""
    comment_count = Comment.objects.count()
    response = author_client.post(URL.edit, data=form_data)
    assertRedirects(response, f'{URL.detail}#comments')
    comment.refresh_from_db()
    new_comment_count = Comment.objects.count()
    assert comment_count == new_comment_count
    assert comment.text == form_data['text']


def test_other_user_cant_edit_comment(admin_client, form_data, news, comment):
    """Проверка редактирования комментария не автором."""
    comment_count = Comment.objects.count()
    comment_text = comment.text
    response = admin_client.post(URL.edit, data=form_data)
    comment.refresh_from_db()
    new_comment_count = Comment.objects.count()
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert new_comment_count == comment_count
    assert comment.text == comment_text


def test_author_can_delete_comment(author_client, form_data, comment):
    """Проверка удаления комментария автором."""
    comment_count = Comment.objects.count() - 1
    response = author_client.delete(URL.delete, data=form_data)
    new_comment_count = Comment.objects.count()
    assertRedirects(response, f'{URL.detail}#comments')
    assert new_comment_count == comment_count


def test_other_user_cant_delete_comment(admin_client, form_data, comment):
    """Проверка удаления комментария не автором."""
    comment_count = Comment.objects.count()
    response = admin_client.delete(URL.delete, data=form_data)
    new_comment_count = Comment.objects.count()
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert new_comment_count == comment_count
