import json

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import ObjetoLaboratorio


class LabObjectsAdminTests(TestCase):
    def setUp(self):
        self.common_user = User.objects.create_user(
            username='leitor',
            password='senha-forte-123',
        )
        self.admin_user = User.objects.create_user(
            username='admin',
            password='senha-forte-123',
            is_staff=True,
        )
        self.object_one = ObjetoLaboratorio.objects.create(
            nome='Microscopio',
            condicao=ObjetoLaboratorio.Condicao.BOM,
            quantidade=2,
            descricao='Microscopio optico.',
        )
        self.object_two = ObjetoLaboratorio.objects.create(
            nome='Fonte Arduino',
            condicao=ObjetoLaboratorio.Condicao.NOVO,
            quantidade=5,
            descricao='Fonte para projetos embarcados.',
        )

    def test_common_user_cannot_access_lab_objects_page(self):
        self.client.force_login(self.common_user)

        response = self.client.get(reverse('admin_lab_objects'))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_staff_user_can_access_lab_objects_page(self):
        self.client.force_login(self.admin_user)

        response = self.client.get(reverse('admin_lab_objects'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Objetos laboratorio')

    def test_config_home_contains_lab_objects_card(self):
        self.client.force_login(self.admin_user)

        response = self.client.get(reverse('admin_config_home'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse('admin_lab_objects'))
        self.assertContains(response, 'Objetos laboratorio')

    def test_api_lists_objects_in_descending_id_order(self):
        self.client.force_login(self.admin_user)

        response = self.client.get(reverse('admin_lab_objects_api'))

        self.assertEqual(response.status_code, 200)
        data = response.json()
        ids = [item['id'] for item in data['objects']]
        self.assertEqual(ids, [self.object_two.id, self.object_one.id])

    def test_api_creates_lab_object(self):
        self.client.force_login(self.admin_user)

        response = self.client.post(
            reverse('admin_lab_objects_api'),
            data=json.dumps({
                'nome': 'Osciloscopio',
                'condicao': ObjetoLaboratorio.Condicao.NOVO,
                'quantidade': 1,
                'descricao': 'Equipamento para leitura de sinais.',
            }),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(ObjetoLaboratorio.objects.filter(nome='Osciloscopio').exists())

    def test_api_rejects_empty_required_fields(self):
        self.client.force_login(self.admin_user)

        response = self.client.post(
            reverse('admin_lab_objects_api'),
            data=json.dumps({
                'nome': '',
                'condicao': '',
                'quantidade': -1,
                'descricao': 'Entrada invalida.',
            }),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('nome', response.json()['errors'])
        self.assertIn('condicao', response.json()['errors'])
        self.assertIn('quantidade', response.json()['errors'])

    def test_api_updates_and_deletes_lab_object(self):
        self.client.force_login(self.admin_user)

        update_response = self.client.post(
            reverse('admin_lab_object_detail_api', args=[self.object_one.id]),
            data=json.dumps({
                'nome': 'Microscopio Atualizado',
                'condicao': ObjetoLaboratorio.Condicao.RUIM,
                'quantidade': 1,
                'descricao': 'Precisa de manutencao.',
            }),
            content_type='application/json',
        )

        self.assertEqual(update_response.status_code, 200)
        self.object_one.refresh_from_db()
        self.assertEqual(self.object_one.nome, 'Microscopio Atualizado')
        self.assertEqual(self.object_one.condicao, ObjetoLaboratorio.Condicao.RUIM)

        delete_response = self.client.delete(reverse('admin_lab_object_detail_api', args=[self.object_one.id]))

        self.assertEqual(delete_response.status_code, 200)
        self.assertFalse(ObjetoLaboratorio.objects.filter(pk=self.object_one.id).exists())

    def test_api_search_filters_by_name(self):
        self.client.force_login(self.admin_user)

        response = self.client.get(reverse('admin_lab_objects_api'), {'q': 'Arduino'})

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data['objects']), 1)
        self.assertEqual(data['objects'][0]['nome'], 'Fonte Arduino')

    def test_exports_csv_and_pdf(self):
        self.client.force_login(self.admin_user)

        csv_response = self.client.get(reverse('admin_lab_objects_export_csv'))
        pdf_response = self.client.get(reverse('admin_lab_objects_export_pdf'))

        self.assertEqual(csv_response.status_code, 200)
        self.assertEqual(csv_response['Content-Type'], 'text/csv; charset=utf-8')
        self.assertContains(csv_response, 'Microscopio')

        self.assertEqual(pdf_response.status_code, 200)
        self.assertEqual(pdf_response['Content-Type'], 'application/pdf')
        self.assertTrue(pdf_response.content.startswith(b'%PDF-1.4'))
