from collections import namedtuple

from django.urls import reverse

FIELD_NAMES = ('title', 'text', 'slug', 'author')
FIELD_DATA = ('Заголовок', 'Текст заметки', 'note-slug')

URL_NAME = namedtuple(
    'NAME',
    [
        'home',
        'add',
        'list',
        'detail',
        'edit',
        'delete',
        'success',
        'login',
        'logout',
        'signup',
    ],
)

URL = URL_NAME(
    reverse('notes:home'),
    reverse('notes:add'),
    reverse('notes:list'),
    reverse('notes:detail', args=('note-slug',)),
    reverse('notes:edit', args=('note-slug',)),
    reverse('notes:delete', args=('note-slug',)),
    reverse('notes:success'),
    reverse('users:login'),
    reverse('users:logout'),
    reverse('users:signup'),
)
