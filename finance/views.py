import json
from datetime import timedelta
from decimal import Decimal

from django.db import models
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import AppointmentForm, TransactionForm
from .models import Appointment, PushSubscription, Transaction


def _safe_next(request, fallback):
    """Só aceita redirecionamento 'next' para URLs do próprio site."""
    nxt = request.POST.get('next', '')
    if nxt and url_has_allowed_host_and_scheme(nxt, allowed_hosts={request.get_host()}):
        return nxt
    return fallback


def list_create(request):
    form = TransactionForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('finance:list')

    qs = Transaction.objects.all().order_by('-date', '-id')
    client_filter = request.GET.get('client', '').strip()
    f_from = request.GET.get('from', '')
    f_to = request.GET.get('to', '')
    if client_filter:
        qs = qs.filter(client__icontains=client_filter)
    if f_from:
        qs = qs.filter(date__gte=f_from)
    if f_to:
        qs = qs.filter(date__lte=f_to)

    totals = qs.aggregate(total_revenue=models.Sum('price'), total_cost=models.Sum('cost'))
    total_revenue = totals['total_revenue'] or Decimal('0')
    total_cost = totals['total_cost'] or Decimal('0')
    total_profit = total_revenue - total_cost

    # Margem de lucro (% da receita que vira lucro) — usada no resumo.
    if total_revenue:
        margin_pct = int(round(total_profit / total_revenue * 100))
    else:
        margin_pct = 0
    margin_bar = max(0, min(100, margin_pct))

    today = timezone.localdate()
    todays_appointments = Appointment.objects.filter(date=today, status='agendado')

    # Reaproveita o que o usuário digitou (POST inválido) ou o pré-preenchimento
    # vindo da agenda ao concluir uma sessão.
    if form.is_bound:
        prefill = {
            'client': form.data.get('client', ''),
            'price': form.data.get('price', ''),
            'description': form.data.get('description', ''),
        }
    else:
        prefill = {
            'client': request.GET.get('p_client', ''),
            'price': request.GET.get('p_price', ''),
            'description': request.GET.get('p_description', ''),
        }

    context = {
        'form': form,
        'transactions': qs,
        'total_revenue': total_revenue,
        'total_cost': total_cost,
        'total_profit': total_profit,
        'margin_pct': margin_pct,
        'margin_bar': margin_bar,
        'filter_client': client_filter,
        'filter_from': f_from,
        'filter_to': f_to,
        'todays_appointments': todays_appointments,
        'prefill': prefill,
        'active_page': 'finance',
    }
    return render(request, 'finance/front.html', context)


@require_POST
def delete_tx(request, pk):
    tx = get_object_or_404(Transaction, pk=pk)
    tx.delete()
    return redirect('finance:list')


def agenda(request):
    form = AppointmentForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('finance:agenda')

    today = timezone.localdate()
    show = request.GET.get('show', 'proximos')

    if show == 'historico':
        qs = Appointment.objects.filter(
            models.Q(date__lt=today) | ~models.Q(status='agendado')
        ).order_by('-date', '-time')
    else:
        qs = Appointment.objects.filter(date__gte=today, status='agendado')

    # agrupa por dia para exibição
    days = []
    for appt in qs:
        if days and days[-1]['date'] == appt.date:
            days[-1]['items'].append(appt)
        else:
            days.append({'date': appt.date, 'items': [appt]})

    context = {
        'form': form,
        'days': days,
        'show': show,
        'today': today,
        'tomorrow': today + timedelta(days=1),
        'todays_count': Appointment.objects.filter(date=today, status='agendado').count(),
        'active_page': 'agenda',
    }
    return render(request, 'finance/agenda.html', context)


@require_POST
def appointment_status(request, pk):
    appt = get_object_or_404(Appointment, pk=pk)
    status = request.POST.get('status')
    if status in ('agendado', 'concluido', 'cancelado'):
        appt.status = status
        appt.save()
    return redirect(_safe_next(request, 'finance:agenda'))


@require_POST
def appointment_delete(request, pk):
    appt = get_object_or_404(Appointment, pk=pk)
    appt.delete()
    return redirect(_safe_next(request, 'finance:agenda'))


# ---------- Notificações push ----------

def service_worker(request):
    # O navegador busca o sw.js em segundo plano (inclusive para atualizações).
    js = """
self.addEventListener('push', function (event) {
  let data = { title: 'Lembrete', body: '' };
  try { data = event.data.json(); } catch (e) {}
  event.waitUntil(self.registration.showNotification(data.title, {
    body: data.body,
    icon: '/static/img/icon.png',
    badge: '/static/img/icon.png',
    lang: 'pt-BR',
  }));
});

self.addEventListener('notificationclick', function (event) {
  event.notification.close();
  event.waitUntil(clients.matchAll({ type: 'window' }).then(function (list) {
    for (const c of list) { if ('focus' in c) return c.focus(); }
    return clients.openWindow('/agenda/');
  }));
});
"""
    return HttpResponse(js, content_type='application/javascript')


def vapid_public_key(request):
    from .webpush import get_public_key
    return JsonResponse({'publicKey': get_public_key()})


@require_POST
def push_subscribe(request):
    try:
        data = json.loads(request.body)
        endpoint = data['endpoint']
    except (json.JSONDecodeError, KeyError):
        return JsonResponse({'ok': False}, status=400)
    PushSubscription.objects.update_or_create(
        endpoint=endpoint,
        defaults={'subscription_json': json.dumps(data)},
    )
    return JsonResponse({'ok': True})


@require_POST
def push_test(request):
    from .webpush import send_push_to_all
    sent = send_push_to_all('🔔 Notificações ativas', 'Você vai receber os lembretes da agenda por aqui.')
    return JsonResponse({'ok': True, 'sent': sent})
