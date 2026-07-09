from decimal import Decimal
from django import template

register = template.Library()


@register.filter
def brl(value):
    """Formata um Decimal/float para o formato brasileiro com separador de milhares '.' e vírgula decimal.

    Ex: Decimal('5000') -> '5.000,00'
    """
    if value is None:
        return '0,00'
    try:
        # garantir Decimal
        v = Decimal(value)
    except Exception:
        try:
            v = Decimal(str(value))
        except Exception:
            return '0,00'
    # formata com separador de milhares americano (',') e ponto decimal, depois inverte para BR
    s = '{:,.2f}'.format(v)
    # troca: '1,234.56' -> '1.234,56'
    s = s.replace(',', 'X').replace('.', ',').replace('X', '.')
    return s
