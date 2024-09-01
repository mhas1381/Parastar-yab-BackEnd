from django.contrib import admin
from .models import Transaction


class TransactionsAdmin(admin.ModelAdmin):
    list_display = ['id', 'amount', 'nurse', 'mode']


admin.site.register(Transaction, TransactionsAdmin)