from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.db import models
from .models import Transaction
from django.urls import reverse

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
            # remover separador de milhares e trocar vírgula decimal para ponto
            clean = v.replace('.', '').replace(',', '.')
            try:
                return Decimal(clean)
            except Exception:
                return Decimal('0')
        Transaction.objects.create(
            client=client,
            date=date,
            description=description,
            price=parse_brl(price),
            cost=parse_brl(cost),
            payment=payment,
            notes=notes,
        )
        return redirect('finance:list')

    qs = Transaction.objects.all().order_by('-date','-id')
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
    }
    return render(request, 'finance/front.html', context)

def delete_tx(request, pk):
    tx = get_object_or_404(Transaction, pk=pk)
    tx.delete()
    return redirect('finance:list')
