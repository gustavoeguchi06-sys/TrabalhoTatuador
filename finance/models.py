from django.db import models


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


class Appointment(models.Model):
    STATUS_CHOICES = [
        ('agendado', 'Agendado'),
        ('concluido', 'Concluído'),
        ('cancelado', 'Cancelado'),
    ]

    client = models.CharField(max_length=200)
    phone = models.CharField(max_length=30, blank=True)
    date = models.DateField()
    time = models.TimeField()
    duration_minutes = models.PositiveIntegerField(default=60)
    description = models.TextField(blank=True)
    estimated_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='agendado')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date', 'time']

    def __str__(self):
        return f"{self.client} - {self.date} {self.time}"


class PushSubscription(models.Model):
    endpoint = models.URLField(max_length=500, unique=True)
    subscription_json = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.endpoint[:60]


class NotificationLog(models.Model):
    """Registra lembretes já enviados para não repetir."""
    KIND_CHOICES = [
        ('daily', 'Resumo do dia'),
        ('hour', '1 hora antes'),
        ('30min', '30 minutos antes'),
    ]

    kind = models.CharField(max_length=10, choices=KIND_CHOICES)
    ref_date = models.DateField()
    appointment = models.ForeignKey(Appointment, null=True, blank=True, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['kind', 'ref_date', 'appointment'], name='unique_reminder'),
        ]
