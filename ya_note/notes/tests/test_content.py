from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from .constants import URL
from notes.models import Note

User = get_user_model()

COUNT_COMMENTS = 10


class TestDetailPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.note = Note.objects.create(
            title='Тестовая новость',
            text='Просто текст.',
            author=cls.author
        )
        cls.edit_url = reverse(
            'notes:edit',
            args=(cls.note.slug,)
        )

    def test_anonymous_no_access_to_the_edit_form(self):
        """Проверка что анониму не доступна страница.
        редактирования.
        """
        response = self.client.get(self.edit_url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_auyhor_access_to_the_edit_form(self):
        """Проверка что автору доступна страница.
        редактирования.
        """
        response = self.author_client.get(self.edit_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_edit_add_form(self):
        """Проверяет что форма передается на страницы редактирования.
        и добавления.
        """
        urls = [
            (URL.add, 'страница добавления'),
            (self.edit_url, 'страница редактирования'),
        ]
        for url, page in urls:
            with self.subTest(page=page):
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
