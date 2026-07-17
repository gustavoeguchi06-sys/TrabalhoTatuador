from decimal import Decimal

from django import forms

from .models import Appointment, Transaction


class BRLDecimalField(forms.DecimalField):
    """Campo decimal que aceita o formato brasileiro (ex: 5.000,00)."""

    def to_python(self, value):
        if isinstance(value, str):
            value = value.strip().replace('.', '').replace(',', '.')
        return super().to_python(value)


class TransactionForm(forms.ModelForm):
    price = BRLDecimalField(
        label='Preço', max_digits=10, decimal_places=2, min_value=Decimal('0'),
        error_messages={'invalid': 'informe um valor válido (ex: 1.500,00).'},
    )
    cost = BRLDecimalField(
        label='Custo', max_digits=10, decimal_places=2, min_value=Decimal('0'), required=False,
        error_messages={'invalid': 'informe um valor válido (ex: 200,00).'},
    )

    class Meta:
        model = Transaction
        fields = ['client', 'date', 'description', 'price', 'cost', 'payment', 'notes']
        labels = {
            'client': 'Cliente',
            'date': 'Data',
            'description': 'Descrição',
            'payment': 'Pagamento',
            'notes': 'Observações',
        }

    def clean_cost(self):
        return self.cleaned_data.get('cost') or Decimal('0')


class AppointmentForm(forms.ModelForm):
    estimated_price = BRLDecimalField(
        label='Valor estimado', max_digits=10, decimal_places=2, min_value=Decimal('0'), required=False,
        error_messages={'invalid': 'informe um valor válido (ex: 500,00).'},
    )

    class Meta:
        model = Appointment
        fields = ['client', 'phone', 'date', 'time', 'duration_minutes',
                  'description', 'estimated_price', 'notes']
        labels = {
            'client': 'Cliente',
            'phone': 'Telefone',
            'date': 'Data',
            'time': 'Horário',
            'duration_minutes': 'Duração',
            'description': 'Descrição',
            'notes': 'Observações',
        }

    def clean_estimated_price(self):
        return self.cleaned_data.get('estimated_price') or Decimal('0')
