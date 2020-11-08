from django.contrib import admin
from elements.models import APR, Transfer, Account, Plan

admin.site.register(APR)
admin.site.register(Account)
admin.site.register(Plan)
admin.site.register(Transfer)