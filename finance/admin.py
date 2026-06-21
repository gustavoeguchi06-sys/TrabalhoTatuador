from django.contrib import admin
from .models import Transaction

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('date','client','price','cost','payment')
    list_filter = ('payment','date')
