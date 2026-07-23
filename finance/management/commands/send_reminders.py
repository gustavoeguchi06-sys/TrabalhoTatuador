"""Roda uma verificação da agenda e envia os lembretes pendentes.

Alternativa ao agendador em thread para uso com cron (ex: Cron Job do Render
a cada 5 minutos): `python manage.py send_reminders`.
O registro em NotificationLog garante que nada é enviado em duplicidade
mesmo com a thread e o cron ativos ao mesmo tempo.
"""
from django.core.management.base import BaseCommand

from finance.reminders import check_and_send


class Command(BaseCommand):
    help = 'Verifica a agenda e envia os lembretes push pendentes (uma passada).'

    def handle(self, *args, **options):
        check_and_send()
        self.stdout.write(self.style.SUCCESS('Verificação de lembretes concluída.'))
