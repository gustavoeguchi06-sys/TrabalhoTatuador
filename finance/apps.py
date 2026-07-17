import os
import sys

from django.apps import AppConfig


class FinanceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'finance'

    def ready(self):
        # Inicia o verificador de lembretes só no processo que serve requisições
        # (evita duplicar no autoreload e rodar durante migrate/tests).
        is_runserver = 'runserver' in sys.argv
        is_reloader_child = os.environ.get('RUN_MAIN') == 'true'
        if is_runserver and not is_reloader_child:
            return
        if any(cmd in sys.argv for cmd in ('migrate', 'makemigrations', 'test', 'shell',
                                           'collectstatic', 'createsuperuser', 'send_reminders')):
            return
        from . import reminders
        reminders.start_scheduler()
