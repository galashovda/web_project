from django.db import models
from django.urls import reverse
from django.db import DatabaseError, transaction

class Genre(models.Model):
    name = models.CharField(
        max_length=200,
        help_text="Введите жанр"
        )

    def __str__(self):
        return self.name


class Language(models.Model):
    name = models.CharField(max_length=200,
                            help_text="Введите естественный язык книги (например, английский, французский, японский и т. д.)")

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey('Author', on_delete=models.SET_NULL, null=True)
    summary = models.TextField(max_length=1000, help_text="Введите краткое описание книги")
    isbn = models.CharField('ISBN', max_length=13,
                            help_text='13 Character <a href="https://www.isbn-international.org/content/what-isbn'
                                      '">ISBN number</a>')
    genre = models.ManyToManyField(Genre, help_text="Выберете жанр")
    language = models.ForeignKey('Language', on_delete=models.SET_NULL, null=True)

    def display_genre(self):
        return ', '.join([genre.name for genre in self.genre.all()[:3]])

    display_genre.short_description = 'Genre'

    
    def get_absolute_url(self):
        return reverse('book-detail', args=[str(self.id)])

    def __str__(self):
        return self.title


import uuid 
from datetime import date

from django.contrib.auth.models import User  


class BookInstance(models.Model):
    """Модель, представляющая собой конкретный экземпляр книги (то есть тот, который можно позаимствовать из библиотеки)."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          help_text="Уникальный идентификатор для этой конкретной книги")
    book = models.ForeignKey('Book', on_delete=models.SET_NULL, null=True)
    imprint = models.CharField(max_length=200)
    due_back = models.DateField(null=True, blank=True)
    borrower = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    @property
    def is_overdue(self):
        if self.due_back and date.today() > self.due_back:
            return True
        return False

    LOAN_STATUS = (
        ('d', 'Maintenance'),
        ('o', 'On loan'),
        ('a', 'Available'),
        ('r', 'Reserved'),
    )

    status = models.CharField(
        max_length=1,
        choices=LOAN_STATUS,
        blank=True,
        default='d',
        help_text='Book availability')

    class Meta:
        ordering = ['due_back']
        permissions = (("can_mark_returned", "Set book as returned"),)


    def __str__(self):
        return '{0} ({1})'.format(self.id, self.book.title)


class Author(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField('died', null=True, blank=True)

    class Meta:
        ordering = ['last_name', 'first_name']

    def get_absolute_url(self):
        """Возвращает URL-адрес для доступа к конкретному экземпляру author."""
        return reverse('author-detail', args=[str(self.id)])

    def __str__(self):
        """Строка для представления объекта модели."""
        return '{0}, {1}'.format(self.last_name, self.first_name)
