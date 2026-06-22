from decimal import Decimal
import re
from django.shortcuts import render, redirect, get_object_or_404
from django.db import models
from .models import Transaction
from django.urls import reverse
from django.views.decorators.http import require_POST
import datetime

def list_create(request):
    if request.method == 'POST':
        client = request.POST.get('client','').strip()
        date = request.POST.get('date') or None
        description = request.POST.get('description','').strip()
        price = request.POST.get('price') or '0'
        cost = request.POST.get('cost') or '0'
        payment = request.POST.get('payment','')
        notes = request.POST.get('notes','')
        # aceitar formato brasileiro: milhares com ponto e decimais com vírgula (ex: 5.000,00)
        def parse_brl(value_str):
            v = (value_str or '').strip()
            if v == '':
                return Decimal('0')
            # remover qualquer caractere que não seja dígito, ponto, vírgula ou sinal
            cleaned = re.sub(r"[^0-9,\.\-]", "", v)
            if cleaned == '':
                return Decimal('0')
            # se existir vírgula e ponto, assumir que pontos são milhares e vírgula decimal
            if cleaned.count(',') == 1 and cleaned.count('.') >= 1:
                cleaned = cleaned.replace('.', '').replace(',', '.')
            else:
                # substituir vírgula por ponto para decimal
                cleaned = cleaned.replace(',', '.')
            try:
                return Decimal(cleaned)
            except Exception:
                return Decimal('0')
        # sanitize client: remove digits
        client_clean = re.sub(r"\d+", "", client).strip()

        price_val = parse_brl(price)
        cost_val = parse_brl(cost)

        # server-side validation: cost must be less than price
        if cost_val >= price_val:
            # prepare context to re-render form with error
            qs = Transaction.objects.all().order_by('-date','-id')
            totals = qs.aggregate(total_revenue=models.Sum('price'), total_cost=models.Sum('cost'))
            total_revenue = totals['total_revenue'] or Decimal('0')
            total_cost = totals['total_cost'] or Decimal('0')
            total_profit = total_revenue - total_cost
            context = {
                'transactions': qs,
                'total_revenue': total_revenue,
                'total_cost': total_cost,
                'total_profit': total_profit,
                'filter_client': '',
                'filter_from': '',
                'filter_to': '',
                'error': 'O custo deve ser menor que o preço cobrado.',
                'form_values': {
                    'client': client,
                    'date': date,
                    'description': description,
                    'price': price,
                    'cost': cost,
                    'payment': payment,
                    'notes': notes,
                }
            }
            return render(request, 'finance/front.html', context)

        # instantiate model and run full_clean to enforce model validation
        tx = Transaction(
            client=client_clean,
            date=date,
            description=description,
            price=price_val,
            cost=cost_val,
            payment=payment,
            notes=notes,
        )
        try:
            tx.full_clean()
            tx.save()
            return redirect('finance:list')
        except Exception as e:
            # if validation error, re-render form with message
            msg = str(e)
            # prefer ValidationError message list if available
            try:
                from django.core.exceptions import ValidationError
                if isinstance(e, ValidationError):
                    msg = '; '.join(e.messages)
            except Exception:
                pass
            qs = Transaction.objects.all().order_by('-date','-id')
            totals = qs.aggregate(total_revenue=models.Sum('price'), total_cost=models.Sum('cost'))
            total_revenue = totals['total_revenue'] or Decimal('0')
            total_cost = totals['total_cost'] or Decimal('0')
            total_profit = total_revenue - total_cost
            context = {
                'transactions': qs,
                'total_revenue': total_revenue,
                'total_cost': total_cost,
                'total_profit': total_profit,
                'filter_client': '',
                'filter_from': '',
                'filter_to': '',
                'error': msg,
                'form_values': {
                    'client': client,
                    'date': date,
                    'description': description,
                    'price': price,
                    'cost': cost,
                    'payment': payment,
                    'notes': notes,
                }
            }
            return render(request, 'finance/front.html', context)

    qs = Transaction.objects.all().order_by('-date','-id')
    # handle view period from session: if set, only show transactions from that month onwards
    view_period = request.session.get('view_period')
    if view_period:
        try:
            year, month = map(int, view_period.split('-'))
            first_day = datetime.date(year, month, 1)
            qs = qs.filter(date__gte=first_day)
        except Exception:
            pass
    client_filter = request.GET.get('client','').strip()
    f_from = request.GET.get('from','')
    f_to = request.GET.get('to','')
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

    context = {
        'transactions': qs,
        'total_revenue': total_revenue,
        'total_cost': total_cost,
        'total_profit': total_profit,
        'filter_client': client_filter,
        'filter_from': f_from,
        'filter_to': f_to,
        'view_period': view_period,
    }
    # auto-reset warning on first day of month if not already shown for this month
    today = datetime.date.today()
    current_ym = f"{today.year:04d}-{today.month:02d}"
    auto_reset_warning = False
    if today.day == 1 and request.session.get('reset_shown_for') != current_ym:
        auto_reset_warning = True
    context['auto_reset_warning'] = auto_reset_warning
    return render(request, 'finance/front.html', context)


@require_POST
def reset_view(request):
    """Set session view_period to current year-month (does not delete DB records)."""
    today = datetime.date.today()
    ym = f"{today.year:04d}-{today.month:02d}"
    request.session['view_period'] = ym
    # mark that reset was shown for this month
    request.session['reset_shown_for'] = ym
    return redirect('finance:list')

def delete_tx(request, pk):
    tx = get_object_or_404(Transaction, pk=pk)
    tx.delete()
    return redirect('finance:list')
