from django.db import models
from django.core.exceptions import ValidationError

class Transaction(models.Model):
    client = models.CharField(max_length=200)
    date = models.DateField()
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.client} - {self.date} - {self.price}"

    def clean(self):
        # ensure cost is strictly less than price
        if self.cost is not None and self.price is not None:
            try:
                if self.cost >= self.price:
                    raise ValidationError('O custo deve ser menor que o preço cobrado.')
            except TypeError:
                # ignore if types are not comparable here; validation will be handled elsewhere
                pass
