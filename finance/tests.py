from datetime import date, time, timedelta
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .forms import AppointmentForm, BRLDecimalField, TransactionForm
from .models import Appointment, NotificationLog, PushSubscription, Transaction


class BRLDecimalFieldTests(TestCase):
    def setUp(self):
        self.field = BRLDecimalField(max_digits=10, decimal_places=2)

    def test_formato_brasileiro(self):
        self.assertEqual(self.field.clean('5.000,00'), Decimal('5000.00'))
        self.assertEqual(self.field.clean('150,50'), Decimal('150.50'))
        self.assertEqual(self.field.clean('80'), Decimal('80'))

    def test_valor_invalido_gera_erro(self):
        with self.assertRaises(Exception):
            self.field.clean('abc')


class TransactionFormTests(TestCase):
    def test_valido_cria_transacao(self):
        form = TransactionForm({
            'client': 'Ana', 'date': '2026-07-17', 'description': 'Braço',
            'price': '1.500,00', 'cost': '', 'payment': 'Pix', 'notes': '',
        })
        self.assertTrue(form.is_valid(), form.errors)
        tx = form.save()
        self.assertEqual(tx.price, Decimal('1500.00'))
        self.assertEqual(tx.cost, Decimal('0'))

    def test_data_vazia_nao_quebra(self):
        form = TransactionForm({'client': 'Ana', 'date': '', 'price': '100,00'})
        self.assertFalse(form.is_valid())
        self.assertIn('date', form.errors)

    def test_preco_invalido_nao_vira_zero(self):
        form = TransactionForm({'client': 'Ana', 'date': '2026-07-17', 'price': 'xyz'})
        self.assertFalse(form.is_valid())
        self.assertIn('price', form.errors)


class AppointmentFormTests(TestCase):
    def test_duracao_invalida_rejeitada(self):
        form = AppointmentForm({
            'client': 'Ana', 'date': '2026-07-17', 'time': '14:00',
            'duration_minutes': 'abc',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('duration_minutes', form.errors)


class AuthRequiredTests(TestCase):
    def test_paginas_redirecionam_para_login(self):
        for name in ('finance:list', 'finance:agenda'):
            resp = self.client.get(reverse(name))
            self.assertEqual(resp.status_code, 302)
            self.assertIn('/accounts/login/', resp.url)

    def test_push_test_exige_login(self):
        resp = self.client.post(reverse('finance:push_test'))
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/accounts/login/', resp.url)

    def test_sw_js_publico(self):
        resp = self.client.get('/sw.js')
        self.assertEqual(resp.status_code, 200)

    def test_login_da_acesso(self):
        User.objects.create_user('tatuador', password='segredo-forte-123')
        self.client.login(username='tatuador', password='segredo-forte-123')
        resp = self.client.get(reverse('finance:list'))
        self.assertEqual(resp.status_code, 200)


class ViewTests(TestCase):
    def setUp(self):
        User.objects.create_user('tatuador', password='segredo-forte-123')
        self.client.login(username='tatuador', password='segredo-forte-123')

    def test_delete_via_get_nao_permitido(self):
        tx = Transaction.objects.create(client='Ana', date=date(2026, 7, 17), price=100)
        resp = self.client.get(reverse('finance:delete', args=[tx.pk]))
        self.assertEqual(resp.status_code, 405)
        self.assertTrue(Transaction.objects.filter(pk=tx.pk).exists())

    def test_delete_via_post_funciona(self):
        tx = Transaction.objects.create(client='Ana', date=date(2026, 7, 17), price=100)
        resp = self.client.post(reverse('finance:delete', args=[tx.pk]))
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(Transaction.objects.filter(pk=tx.pk).exists())

    def test_post_invalido_reexibe_erros(self):
        resp = self.client.post(reverse('finance:list'), {'client': '', 'date': '', 'price': ''})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Corrija os campos abaixo')
        self.assertEqual(Transaction.objects.count(), 0)

    def test_totais(self):
        Transaction.objects.create(client='Ana', date=date(2026, 7, 17), price=1000, cost=200)
        Transaction.objects.create(client='Bia', date=date(2026, 7, 16), price=500, cost=100)
        resp = self.client.get(reverse('finance:list'))
        self.assertEqual(resp.context['total_revenue'], Decimal('1500'))
        self.assertEqual(resp.context['total_cost'], Decimal('300'))
        self.assertEqual(resp.context['total_profit'], Decimal('1200'))

    def test_next_externo_ignorado(self):
        appt = Appointment.objects.create(client='Ana', date=date(2026, 7, 17), time=time(14, 0))
        resp = self.client.post(
            reverse('finance:appointment_status', args=[appt.pk]),
            {'status': 'concluido', 'next': 'https://evil.example.com/'},
        )
        self.assertEqual(resp.status_code, 302)
        self.assertNotIn('evil.example.com', resp.url)


class ReminderTests(TestCase):
    def _subscribe(self):
        PushSubscription.objects.create(endpoint='https://push.example/1', subscription_json='{}')

    @patch('finance.webpush.send_push_to_all', return_value=1)
    def test_lembrete_uma_hora_antes_sem_duplicar(self, mock_send):
        from .reminders import check_and_send
        self._subscribe()
        now = timezone.localtime()
        start = now + timedelta(minutes=45)
        # Evita virada de dia perto da meia-noite: só roda se a sessão cai hoje.
        if start.date() != now.date():
            self.skipTest('perto da meia-noite')
        Appointment.objects.create(client='Ana', date=start.date(), time=start.time())
        check_and_send()
        check_and_send()
        kinds = list(NotificationLog.objects.values_list('kind', flat=True))
        self.assertEqual(kinds.count('hour'), 1)

    @patch('finance.webpush.send_push_to_all', return_value=1)
    def test_sem_inscricao_nao_faz_nada(self, mock_send):
        from .reminders import check_and_send
        check_and_send()
        self.assertEqual(NotificationLog.objects.count(), 0)
        mock_send.assert_not_called()
