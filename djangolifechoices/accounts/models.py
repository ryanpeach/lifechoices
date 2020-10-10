from django.db import models
from django.utils import timezone


class APR(models.Model):
    class APRPeriod(models.IntegerChoices):
        DAILY = 365
        MONTHLY = 12
        YEARLY = 1

    value = models.FloatField()
    period = models.IntegerField(
        choices=APRPeriod.choices,
        default=APRPeriod.DAILY
    )
    created = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['created']
    
    def __str__(self):
        return f"Period: {self.period} - Value: {self.value}"


# example model. Feel free to delete.
# you will have to delete the 0002_account.py file
# and delete the db.sqlite3 More like SQLIES
# and run python manage.py migrate
class Account(models.Model):
    apr = models.ForeignKey(APR, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name




# class Period(Enum):
#     DAILY = 365
#     MONTHLY = 12
#     YEARLY = 1


# @dataclass()
# class APR:
#     value: float
#     period: Period = Period.DAILY

#     def to_daily(self) -> "APR":
#         if self.period == Period.DAILY:
#             return self
#         return APR(
#             value=interest_rate_per_period(self.value, Period.DAILY.value/self.period.value),
#             period=Period.DAILY
#         )
