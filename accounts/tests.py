from django.contrib.auth import get_user
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from book.models import Books
from .models import UserProfile


class LoginViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='test',
            email='test@example.com',
            password='senha-forte-123',
        )

    def test_common_user_can_login_with_username_and_redirects_to_home(self):
        response = self.client.post(reverse('login'), {
            'username': 'test',
            'password': 'senha-forte-123',
        })

        self.assertRedirects(response, reverse('home'))
        self.assertTrue(get_user(self.client).is_authenticated)
        self.assertFalse(get_user(self.client).is_superuser)

    def test_common_user_can_login_with_email_and_redirects_to_home(self):
        response = self.client.post(reverse('login'), {
            'username': 'test@example.com',
            'password': 'senha-forte-123',
        })

        self.assertRedirects(response, reverse('home'))
        self.assertTrue(get_user(self.client).is_authenticated)
        self.assertFalse(get_user(self.client).is_superuser)

    def test_profile_requires_only_authenticated_common_user(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse('perfil'))

        self.assertEqual(response.status_code, 200)
        self.assertFalse(get_user(self.client).is_superuser)

    def test_common_user_does_not_see_config_button_on_home(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, reverse('admin_config_home'))
        self.assertNotContains(response, 'Configurações')

    def test_logout_redirects_to_home(self):
        self.client.force_login(self.user)

        response = self.client.post(reverse('logout'))

        self.assertRedirects(response, reverse('home'))
        self.assertFalse(get_user(self.client).is_authenticated)

    def test_register_creates_user_profile(self):
        response = self.client.post(reverse('register'), {
            'username': 'novo_leitor',
            'email': 'novo_leitor@example.com',
            'sexo': UserProfile.Sexo.FEMININO,
            'matricula': '20260001',
            'password1': 'senha-forte-123',
            'password2': 'senha-forte-123',
        })

        self.assertRedirects(response, reverse('all_books'))
        user = User.objects.get(username='novo_leitor')
        self.assertEqual(user.profile.sexo, UserProfile.Sexo.FEMININO)
        self.assertEqual(user.profile.matricula, '20260001')


class AdminConfigTests(TestCase):
    def setUp(self):
        self.common_user = User.objects.create_user(
            username='leitor',
            email='leitor@example.com',
            password='senha-forte-123',
        )
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='senha-forte-123',
            is_staff=True,
        )
        self.book = Books.objects.create(
            titulo='Livro Inicial',
            autor='Autor Inicial',
            editora='Editora Inicial',
            ano_publicacao=2024,
            resumo='Resumo inicial',
        )

    def test_common_user_cannot_access_config_pages(self):
        self.client.force_login(self.common_user)

        response = self.client.get(reverse('admin_config_home'))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_staff_user_can_access_config_home(self):
        self.client.force_login(self.admin_user)

        response = self.client.get(reverse('admin_config_home'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Configuracoes do sistema')

    def test_staff_user_sees_config_button_on_home(self):
        self.client.force_login(self.admin_user)

        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse('admin_config_home'))
        self.assertContains(response, 'Configurações')

    def test_staff_user_can_render_management_menus(self):
        self.client.force_login(self.admin_user)

        urls = [
            reverse('admin_books'),
            f"{reverse('admin_books')}?action=create",
            f"{reverse('admin_books')}?action=edit&book={self.book.id}",
            f"{reverse('admin_books')}?action=delete&book={self.book.id}",
            reverse('admin_users'),
            f"{reverse('admin_users')}?action=create",
            f"{reverse('admin_users')}?action=edit&user={self.common_user.id}",
            f"{reverse('admin_users')}?action=delete&user={self.common_user.id}",
        ]

        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_action_menu_only_shows_list_and_create_actions(self):
        self.client.force_login(self.admin_user)

        pages = [reverse('admin_books'), reverse('admin_users')]

        for url in pages:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertContains(response, '<section class="action-menu"', html=False)
                self.assertContains(response, '>Listar<', html=False)
                self.assertContains(response, '>Adicionar<', html=False)
                self.assertNotContains(response, '<span class="">Editar</span>', html=True)
                self.assertNotContains(response, '<span class="">Remover</span>', html=True)

    def test_staff_user_can_create_edit_and_delete_book(self):
        self.client.force_login(self.admin_user)

        create_response = self.client.post(reverse('admin_books'), {
            'action': 'create',
            'titulo': 'Novo Livro',
            'autor': 'Nova Autora',
            'editora': 'UESPI',
            'ano_publicacao': 2025,
            'resumo': 'Livro criado pelo teste.',
        })
        self.assertRedirects(create_response, reverse('admin_books'))
        created_book = Books.objects.get(titulo='Novo Livro')

        edit_response = self.client.post(reverse('admin_books'), {
            'action': 'edit',
            'book_id': created_book.id,
            'titulo': 'Novo Livro Editado',
            'autor': 'Nova Autora',
            'editora': 'UESPI',
            'ano_publicacao': 2026,
            'resumo': 'Livro editado pelo teste.',
        })
        self.assertRedirects(edit_response, reverse('admin_books'))
        created_book.refresh_from_db()
        self.assertEqual(created_book.titulo, 'Novo Livro Editado')

        delete_response = self.client.post(reverse('admin_books'), {
            'action': 'delete',
            'book_id': created_book.id,
        })
        self.assertRedirects(delete_response, reverse('admin_books'))
        self.assertFalse(Books.objects.filter(pk=created_book.id).exists())

    def test_staff_user_can_create_edit_and_delete_user(self):
        self.client.force_login(self.admin_user)

        create_response = self.client.post(reverse('admin_users'), {
            'action': 'create',
            'username': 'novo_usuario',
            'email': 'novo@example.com',
            'first_name': 'Novo',
            'last_name': 'Usuario',
            'password': 'senha-forte-123',
            'sexo': UserProfile.Sexo.MASCULINO,
            'matricula': '20260002',
        })
        self.assertRedirects(create_response, reverse('admin_users'))
        created_user = User.objects.get(username='novo_usuario')
        self.assertTrue(created_user.is_active)
        self.assertFalse(created_user.is_staff)
        self.assertTrue(created_user.check_password('senha-forte-123'))
        self.assertEqual(created_user.profile.sexo, UserProfile.Sexo.MASCULINO)
        self.assertEqual(created_user.profile.matricula, '20260002')

        edit_response = self.client.post(reverse('admin_users'), {
            'action': 'edit',
            'user_id': created_user.id,
            'username': 'usuario_editado',
            'email': 'editado@example.com',
            'first_name': 'Usuario',
            'last_name': 'Editado',
            'is_staff': 'on',
            'sexo': UserProfile.Sexo.OUTRO,
            'matricula': '20260003',
        })
        self.assertRedirects(edit_response, reverse('admin_users'))
        created_user.refresh_from_db()
        self.assertEqual(created_user.username, 'usuario_editado')
        self.assertTrue(created_user.is_staff)
        self.assertEqual(created_user.profile.sexo, UserProfile.Sexo.OUTRO)
        self.assertEqual(created_user.profile.matricula, '20260003')

        delete_response = self.client.post(reverse('admin_users'), {
            'action': 'delete',
            'user_id': created_user.id,
        })
        self.assertRedirects(delete_response, reverse('admin_users'))
        self.assertFalse(User.objects.filter(pk=created_user.id).exists())
