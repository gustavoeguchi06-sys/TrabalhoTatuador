from django.contrib import admin
from .models import Appointment, NotificationLog, PushSubscription, Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('date', 'client', 'price', 'cost', 'payment')
    list_filter = ('payment', 'date')


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('date', 'time', 'client', 'status', 'estimated_price')
    list_filter = ('status', 'date')


@admin.register(PushSubscription)
class PushSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('endpoint', 'created')


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ('kind', 'ref_date', 'appointment', 'created')
    list_filter = ('kind',)
