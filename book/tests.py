from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

from .models import Books


class SearchBookTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='leitor',
            password='senha-forte-123',
        )
        self.book_one = Books.objects.create(
            titulo='Algoritmos',
            autor='Autor Um',
            editora='UESPI',
            ano_publicacao=2024,
            resumo='Livro de algoritmos.',
        )
        self.book_two = Books.objects.create(
            titulo='Banco de Dados',
            autor='Autor Dois',
            editora='UESPI',
            ano_publicacao=2025,
            resumo='Livro de banco de dados.',
        )

    def test_empty_search_returns_all_cataloged_books(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse('search_book'), {'q': ''})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.book_one.titulo)
        self.assertContains(response, self.book_two.titulo)
        self.assertEqual(list(response.context['books']), [self.book_one, self.book_two])

    def test_blank_search_returns_all_cataloged_books(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse('search_book'), {'q': '   '})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.book_one.titulo)
        self.assertContains(response, self.book_two.titulo)

    def test_search_with_text_filters_by_title(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse('search_book'), {'q': 'Algoritmos'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.book_one.titulo)
        self.assertNotContains(response, self.book_two.titulo)
