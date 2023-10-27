from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from .constants import URL, FIELD_NAMES, FIELD_DATA
from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.user = User.objects.create(username='Пользователь')
        cls.user_client = Client()
        cls.user_client.force_login(cls.user)
        cls.note = Note.objects.create(
            **dict(zip(FIELD_NAMES, (*FIELD_DATA, cls.author)))
        )

    def test_pages_availability_for_anonymous_user(self):
        """Проверка доступа к страницам."""
        urls = (
            (URL.home, self.client, HTTPStatus.OK, 'Аноним'),
            (URL.login, self.client, HTTPStatus.OK, 'Аноним'),
            (URL.logout, self.client, HTTPStatus.OK, 'Аноним'),
            (URL.signup, self.client, HTTPStatus.OK, 'Аноним'),
            (URL.detail, self.author_client, HTTPStatus.OK, 'Автор'),
            (URL.edit, self.author_client, HTTPStatus.OK, 'Автор'),
            (URL.delete, self.author_client, HTTPStatus.OK, 'Автор'),
            (URL.add, self.user_client, HTTPStatus.OK, 'Пользователь'),
            (URL.list, self.user_client, HTTPStatus.OK, 'Пользователь'),
            (URL.success, self.user_client, HTTPStatus.OK, 'Пользователь'),
            (
                URL.detail,
                self.user_client,
                HTTPStatus.NOT_FOUND,
                'Пользователь'
            ),
            (URL.edit, self.user_client, HTTPStatus.NOT_FOUND, 'Пользователь'),
            (
                URL.delete,
                self.user_client,
                HTTPStatus.NOT_FOUND,
                'Пользователь'
            ),
        )
        for url, client, expected_status, user in urls:
            with self.subTest(url=url):
                self.assertEqual(
                    client.get(url).status_code,
                    expected_status,
                )

    def test_redirects(self):
        urls = (
            URL.list,
            URL.add,
            URL.success,
            URL.detail,
            URL.edit,
            URL.delete,
        )
        for url in urls:
            with self.subTest(url=url):
                redirect_url = f'{URL.login}?next={url}'
                self.assertRedirects(
                    self.client.get(url),
                    redirect_url,
                )
