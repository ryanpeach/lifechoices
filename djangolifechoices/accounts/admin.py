from django.contrib import admin
from accounts.models import APR, Transfer, Account, Plan, DateBridge, ValueBridge, DateValueGoal, DateValueGoalVariable, DateValueGoalConstraint

admin.site.register(APR)
admin.site.register(Account)
admin.site.register(Plan)
admin.site.register(Transfer)
admin.site.register(DateBridge)
admin.site.register(DateValueGoal)
admin.site.register(DateValueGoalVariable)
admin.site.register(DateValueGoalConstraint)