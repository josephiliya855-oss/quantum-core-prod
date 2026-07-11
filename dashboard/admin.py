from django.contrib import admin
from .models import AccountState, LedgerHistory

admin.site.register(AccountState)
admin.site.register(LedgerHistory)
