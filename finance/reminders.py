"""Verificação periódica da agenda e envio dos lembretes push.

Regras (horário local, America/Sao_Paulo):
- A partir das 08:00: "Hoje você tem N atendimentos." (uma vez por dia)
- 60 min antes de cada sessão: "Você tem uma tatuagem às HH:MM."
- 30 min antes de cada sessão: "Sua próxima sessão é em 30 minutos."
"""
import logging
import threading
import time as time_mod
from datetime import datetime, timedelta

from django.db import IntegrityError
from django.utils import timezone

logger = logging.getLogger(__name__)

CHECK_INTERVAL_SECONDS = 60
DAILY_SUMMARY_HOUR = 8


def _already_sent(kind, ref_date, appointment=None):
    from .models import NotificationLog
    return NotificationLog.objects.filter(kind=kind, ref_date=ref_date, appointment=appointment).exists()


def _mark_sent(kind, ref_date, appointment=None):
    from .models import NotificationLog
    try:
        NotificationLog.objects.create(kind=kind, ref_date=ref_date, appointment=appointment)
        return True
    except IntegrityError:
        return False


def check_and_send():
    from .models import Appointment, PushSubscription
    from .webpush import send_push_to_all

    if not PushSubscription.objects.exists():
        return

    now = timezone.localtime()
    today = now.date()

    todays = Appointment.objects.filter(date=today, status='agendado')

    # Resumo do dia
    if now.hour >= DAILY_SUMMARY_HOUR and not _already_sent('daily', today):
        count = todays.count()
        if count > 0 and _mark_sent('daily', today):
            plural = 'atendimentos' if count > 1 else 'atendimento'
            send_push_to_all('🗓️ Agenda de hoje', f'Hoje você tem {count} {plural}.')

    # Lembretes por sessão
    tz = timezone.get_current_timezone()
    for appt in todays:
        start = datetime.combine(appt.date, appt.time, tzinfo=tz)
        minutes_left = (start - now).total_seconds() / 60
        hhmm = appt.time.strftime('%H:%M')

        if 30 < minutes_left <= 60 and not _already_sent('hour', today, appt):
            if _mark_sent('hour', today, appt):
                send_push_to_all('🔔 Tatuagem em breve', f'Você tem uma tatuagem às {hhmm}. Cliente: {appt.client}.')

        if 0 < minutes_left <= 30 and not _already_sent('30min', today, appt):
            if _mark_sent('30min', today, appt):
                send_push_to_all('🔔 Próxima sessão', f'Sua próxima sessão é em {int(minutes_left)} minutos ({hhmm} - {appt.client}).')


def _loop():
    while True:
        try:
            check_and_send()
        except Exception:
            logger.exception('Erro ao verificar lembretes')
        time_mod.sleep(CHECK_INTERVAL_SECONDS)


_started = False


def start_scheduler():
    global _started
    if _started:
        return
    _started = True
    thread = threading.Thread(target=_loop, name='reminder-scheduler', daemon=True)
    thread.start()
