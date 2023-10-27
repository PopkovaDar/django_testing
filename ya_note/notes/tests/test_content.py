from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .constants import URL
from notes.models import Note

User = get_user_model()

COUNT_COMMENTS = 10


class TestDetailPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username=' Лев Толстой')
        cls.reader = User.objects.create(username='Читатель')
        cls.note = Note.objects.create(
            title='Тестовая новость',
            text='Просто текст.',
            author=cls.author
        )
        cls.edit_url = reverse(
            'notes:edit',
            args=(cls.note.slug,)
        )

    def test_anonymous_client_has_no_editform(self):
        # Проверка что анониму не доступна страница.
        # редактирования.
        response = self.client.get(self.edit_url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_authorized_client_has_editform(self):
        # Проверка что автору доступна страница.
        # редактирования.
        self.client.force_login(self.author)
        response = self.client.get(self.edit_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_add_form(self):
        # Проверяет что форма передается на страницу добавления.
        self.client.force_login(self.author)
        response = self.client.get(URL.add)
        self.assertIn('form', response.context)

    def test_pages_edit_form(self):
        # Проверяет что форма передается на страницу редактирования.
        self.client.force_login(self.author)
        response = self.client.get(self.edit_url)
        self.assertIn('form', response.context)
