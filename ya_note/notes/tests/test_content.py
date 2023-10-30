from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

from .constants import URL

User = get_user_model()


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
                form = response.context['form']
                self.assertIsInstance(form, NoteForm)


class TestNoteModel(TestCase):
    URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.other_user = User.objects.create(username='Просто пользователь')
        cls.other_client = Client()
        cls.other_client.force_login(cls.other_user)
        cls.note = Note.objects.create(
            title='Тестовая новость',
            text='Просто текст.',
            author=cls.author
        )
        cls.note2 = Note.objects.create(title='Title1',
                                        text='Text1',
                                        author=cls.reader)

    def test_note_passed_to_note_list(self):
        """Тест проверяет что отдельная заметка передаётся на страницу.
        со списком заметок.
        """
        response = self.author_client.get(URL.list)
        self.assertIn('object_list', response.context)
        notes_list = list(response.context['object_list'])
        self.assertIsNotNone(response.context)
        self.assertIn(self.note, notes_list)

    def test_notes_list_for_different_users(self):
        """Тест проверяет что в список заметок одного пользователя не попадают.
        заметки другого пользователя.
        """
        user_clients = (
            (self.author_client, True),
            (self.other_client, False),
        )
        for user_client, notes_has_note in user_clients:
            with self.subTest(name=user_client):
                response = user_client.get(self.URL)
                self.assertIn('object_list', response.context)
                notes = response.context['object_list']
                self.assertEqual(self.note in notes, notes_has_note)
