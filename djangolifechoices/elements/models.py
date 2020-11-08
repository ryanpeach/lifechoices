from django.db import models
from django import forms
from django.utils import timezone
from django.contrib.auth.models import User


# =============== Basics ==================

class APR(models.Model):
    class APRPeriod(models.IntegerChoices):
        DAILY = 365
        MONTHLY = 12
        YEARLY = 1

    value = models.FloatField(default=0)
    period = models.IntegerField(
        choices=APRPeriod.choices,
        default=APRPeriod.DAILY
    )
    created = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['created']
    
    def __str__(self):
        return f"Period: {self.period} - Value: {self.value}"


class PublishedManger(models.Manager):
    def get_queryset(self):
        return super(PublishedManager, self).get_queryset().filter(status='published')


class Plan(models.Model):
    """ Just the name of our plan """
    name = models.CharField(max_length=255, unique=True, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now)
    objects = models.Manager() # default manager
    published = PublishedManger # published manager
    
    class Meta:
        ordering = ['created', 'name']

    def __str__(self):
        return f"Plan: {self.name}"


class Account(models.Model):
    """
    An account like a bank account, or an asset,
    which can change over time with an APR,
    or be transfered to and from.
    """
    name = models.CharField(max_length=255, unique=True, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, null=True)
    amount = models.FloatField(default=0)
    apr = models.ForeignKey(APR, on_delete=models.SET_NULL, null=True)
    created = models.DateTimeField(auto_now=True, editable=False)
    
    class Meta:
        ordering = ['created', 'name']
    
    def __str__(self):
        return f"Account: {self.name}"


class Transfer(models.Model):
    """
    A transfer is a movement of money between two accounts.
    If an account is "None" it implies it is an external account, like lost money or spent money.
    Positive amounts flow from the to_account to the from_account.
    Negative amounts transfer backwards.
    """
    name = models.CharField(max_length=255, unique=True, primary_key=True)
    #user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, default="none")
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, null=True)
    amount = models.FloatField(default=0)
    as_percentage = models.BooleanField(default=False)
    apr = models.ForeignKey(APR, on_delete=models.SET_NULL, null=True)
    start_date = models.DateTimeField(default=timezone.now)
    to_account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, related_name="+")
    from_account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, related_name="+")
    repeat_n = models.IntegerField(default=1)
    created = models.DateTimeField(auto_now=True, editable=False)

    # The types of transfers availible
    ATSTART = "SS"
    DAILY = 'DD'
    NDAILY = 'ND'
    WEEKLY = 'WW'
    NWEEKLY = 'NW'
    MONTHLY = 'MM'
    NMONTHLY = 'NM'
    YEARLY = 'YY'
    NYEARLY = "NY"
    KINDS = {
        ATSTART: "Start",
        DAILY: "Daily",
        NDAILY: "NDaily",
        WEEKLY: "Weekly",
        NWEEKLY: "NWeekly",
        MONTHLY: "Monthly",
        NMONTHLY: "NMonthly",
        YEARLY: "Yearly",
        NYEARLY: "NYearly",
    }
    interval = models.CharField(
        max_length=2,
        choices=list(KINDS.items()),
        default=ATSTART,
    )

    # TODO: Add data validation

    def __str__(self):
        return f"Transfer: {self.name}, Interval: {self.interval}"

    class Meta:
        ordering = ['created', 'name']


# ============== Bridges =============
#
# class DateBridge(models.Model):
#     """ A bridge that activates on a certain date """
#     name = models.CharField(max_length=255, unique=True, primary_key=True)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     activates_on = models.DateField(default=timezone.now)
#     from_plan = models.ForeignKey(Plan, on_delete=models.CASCADE, null=False, related_name="+")
#     to_plan = models.ForeignKey(Plan, on_delete=models.CASCADE, null=False, related_name="+")
#     created = models.DateTimeField(auto_now=True, editable=False)
#
#
# class ValueBridge(models.Model):
#     """ A bridge that activates after a certain account value is reached. """
#     name = models.CharField(max_length=255, unique=True, primary_key=True)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     from_account = models.ForeignKey(Account, on_delete=models.CASCADE, null=False, related_name="+")
#     activates_at = models.FloatField(default=0.0)
#     from_plan = models.ForeignKey(Plan, on_delete=models.CASCADE, null=False, related_name="+")
#     to_plan = models.ForeignKey(Plan, on_delete=models.CASCADE, null=False, related_name="+")
#     created = models.DateTimeField(auto_now=True, editable=False)


# ============ Goals =============

# class DateValueGoal(models.Model):
#     """ A goal for an account to reach a certain value by a certain date. """
#     name = models.CharField(max_length=255, unique=True, primary_key=True)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     account = models.ForeignKey(Account, on_delete=models.CASCADE, null=False, related_name="+")
#     goal_amount = models.FloatField(default=0.0)
#     by_date = models.DateField(default=timezone.now)
#     created = models.DateTimeField(auto_now=True, editable=False)
#
#
# class DateValueGoalVariable(models.Model):
#     """ A list of transfers you can edit to reach your goal. """
#     goal = models.ForeignKey(DateValueGoal, on_delete=models.CASCADE, null=False, related_name="+")
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     transfer = models.ForeignKey(Transfer, on_delete=models.CASCADE, null=False, related_name="+")
#     top_range = models.FloatField(default=0.0)
#     bottom_range = models.FloatField(default=0.0)
#     created = models.DateTimeField(auto_now=True, editable=False)
#
#
# class DateValueGoalConstraint(models.Model):
#     """ A list of accounts you must maintain to reach your goal. """
#     goal = models.ForeignKey(DateValueGoal, on_delete=models.CASCADE, null=False, related_name="+")
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     account = models.ForeignKey(Account, on_delete=models.CASCADE, null=False, related_name="+")
#     top_range = models.FloatField(default=0.0)
#     bottom_range = models.FloatField(default=0.0)
#     created = models.DateTimeField(auto_now=True, editable=False)
