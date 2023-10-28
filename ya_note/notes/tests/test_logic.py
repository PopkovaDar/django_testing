from http import HTTPStatus

from pytils.translit import slugify

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from .constants import URL
from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestCommentCreation(TestCase):
    COMMENT_TITLE = 'Текст заголовка'
    COMMENT_TEXT = 'Текст комментария'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Первый автор')
        cls.second_author = User.objects.create(username='Второй автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.auth_author = Client()
        cls.auth_author.force_login(cls.second_author)
        cls.form_data = {
            'title': cls.COMMENT_TITLE,
            'text': cls.COMMENT_TEXT,
            'slug': 'slug1'}
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='slug',
            author=cls.author,
        )
        cls.form_data_no_slug = {
            'title': cls.COMMENT_TITLE,
            'text': cls.COMMENT_TEXT,
        }

    def test_anonymous_user_cant_create_notes(self):
        """Может ли аноним создать заметку."""
        notes_count = Note.objects.count()
        self.client.post(URL.add, data=self.form_data)
        now_notes_count = Note.objects.count()
        self.assertEqual(now_notes_count, notes_count)

    def test_user_can_create_notes(self):
        """Может ли авторизованный создать заметку."""
        notes_count = Note.objects.count()
        response = self.auth_author.post(URL.add, data=self.form_data)
        self.assertRedirects(response, URL.success)
        now_notes_count = Note.objects.count()
        self.assertEqual(now_notes_count - notes_count, 1)
        note = Note.objects.latest('id')
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.slug, self.form_data['slug'])
        self.assertEqual(note.author, self.second_author)

    def test_not_unique_slug(self):
        """Проверка слага при создании заметки."""
        slug_notes = set(Note.objects.all())
        self.form_data['slug'] = self.note.slug
        response = self.auth_author.post(URL.add, data=self.form_data)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=(self.note.slug + WARNING)
        )
        now_slug_notes = set(Note.objects.all())
        assert slug_notes == now_slug_notes

    def test_empty_slug(self):
        """Проверка при отсутствии слага."""
        self.form_data.pop('slug')
        notes_count = Note.objects.count()
        response = self.auth_author.post(URL.add, data=self.form_data)
        notes_count_after = Note.objects.count()
        new_note = Note.objects.latest('id')
        expected_slug = slugify(self.form_data['title'])
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(notes_count_after - notes_count, 1)
        self.assertEqual(new_note.slug, expected_slug)


class TestCommentEditDelete(TestCase):
    NEW_COMMENT_TITLE = 'Новый заголовок'
    NEW_COMMENT_TEXT = 'Новый текст'
    NEW_COMMENT_SLUG = 'slug1'
    COMMENT_TITLE = 'Заголовок'
    COMMENT_TEXT = 'Текст'
    COMMENT_SLUG = 'slug'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.form_data = {
            'title': cls.NEW_COMMENT_TITLE,
            'text': cls.NEW_COMMENT_TEXT,
            'slug': cls.NEW_COMMENT_SLUG}
        cls.note_author = Note.objects.create(
            title=cls.COMMENT_TITLE,
            text=cls.COMMENT_TEXT,
            slug=cls.COMMENT_SLUG,
            author=cls.author,
        )
        cls.edit_url = reverse('notes:edit', args=(cls.note_author.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note_author.slug,))

    def test_author_can_delete_note(self):
        comments_count = Note.objects.count() - 1
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, URL.success)
        now_comments_count = Note.objects.count()
        self.assertEqual(now_comments_count, comments_count)

    def test_user_cant_delete_note_of_another_user(self):
        """Выполняем запрос на удаление от пользователя-читателя.
        Убедимся, что комментарий по-прежнему на месте.
        """
        comments_count = Note.objects.count()
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        now_comments_count = Note.objects.count()
        self.assertEqual(comments_count, now_comments_count)

    def test_author_can_edit_comment(self):
        """Выполняем запрос на редактирование от имени автора комментария.
        Проверяем, что текст комментария соответствует обновленному.
        """
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.note_author.refresh_from_db()
        self.assertEqual(self.note_author.text, self.NEW_COMMENT_TEXT)
        self.assertEqual(self.note_author.author, self.author)
        self.assertEqual(self.note_author.slug, self.NEW_COMMENT_SLUG)
        self.assertEqual(self.note_author.title, self.NEW_COMMENT_TITLE)
        self.assertEqual(self.note_author.text, self.NEW_COMMENT_TEXT)

    def test_user_cant_edit_comment_of_another_user(self):
        """Отправляем запрос от другого автора, обновляем объект комментария.
        Проверяем, что текст остался тем же, что и был.
        """
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note_author.refresh_from_db()
        self.assertEqual(self.note_author.author, self.author)
        self.assertEqual(self.note_author.slug, self.COMMENT_SLUG)
        self.assertEqual(self.note_author.title, self.COMMENT_TITLE)
        self.assertEqual(self.note_author.text, self.COMMENT_TEXT)
