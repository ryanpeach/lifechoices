from datetime import datetime
from dataclasses import dataclass
from typing import List, Callable, Optional, Dict
from enum import Enum

from lifechoices.utils import interest_rate_per_period


class Period(Enum):
    DAILY = 365
    MONTHLY = 12
    YEARLY = 1


@dataclass()
class APR:
    value: float
    period: Period = Period.DAILY

    def to_daily(self) -> "APR":
        if self.period == Period.DAILY:
            return self
        return APR(
            value=interest_rate_per_period(self.value, Period.DAILY.value/self.period.value),
            period=Period.DAILY
        )


@dataclass()
class Account:
    """
    An account like a bank account, or an asset,
    which can change over time with an APR,
    or be transfered to and from.
    """
    name: str
    amount: float
    APR: APR
    created_on: datetime


@dataclass()
class Transfer:
    """
    A transfer is a movement of money between two accounts.
    If an account is "None" it implies it is an external account, like lost money or spent money.
    Positive amounts flow from the to_account to the from_account.
    Negative amounts transfer backwards.
    """
    name: str
    amount: float
    to_account: Optional[str]
    from_account: Optional[str] = None

    def check(self):
        """ Used to check the values are valid. """
        if self.amount == 0.0:
            return ValueError("Amount should not be zero.")
        if self.to_account == self.from_account:
            return ValueError(f"to_account and from_account should not be equal. Got {self.to_account}")


@dataclass()
class Plan:
    """ A list of accounts and transfers that you plan to make over a period of life. """
    accounts: List[Account]
    transfers: List[Transfer]


@dataclass()
class Bridge:
    """
    Represents as a function which takes a plan and returns a plan.
    """
    name: str
    bridge_function: Callable[[Plan], Plan]

    def __call__(self, oldPlan: Plan):
        return self.bridge_function(oldPlan)


@dataclass()
class DateBridge(Bridge):
    """
    A date on which a plan changes into a new plan.
    Bridges could be buying a house, changing jobs, retiring, etc.
    """
    trigger_date: datetime


@dataclass()
class CallbackBridge(Bridge):
    """
    A logical operation on which a plan changes into a new plan.
    Represented as a function which takes a plan and returns a plan.
    Callback Bridges could be something like "When I pay off my house..."
    """
    trigger_function: Callable[[Dict[str, float]], bool]


@dataclass()
class Once(Transfer):
    """
    Used to indicate transfers happening exactly once on date provided.
    """
    date: datetime = datetime.now()


@dataclass()
class Daily(Transfer):
    """
    Used to indicate transfers every day
    and increasing at APR daily compounded.
    """
    APR: APR = APR(0)


@dataclass()
class Weekly(Transfer):
    """
    Used to indicate transfers every week
    done on the dayOfWeek starting at 0 for Monday
    and increasing at APR daily compounded.
    """
    dayOfWeek: int = 0  # From Monday
    APR: APR = APR(0)

    def check(self):
        """ Check that all values are valid. """
        if not (0 <= self.dayOfWeek <= 6):
            raise ValueError(f"dayOfWeek should be between 0 (Monday) and 6 (Sunday). Got {self.dayOfWeek}")


@dataclass()
class BiWeekly(Transfer):
    """
    Used to indicate transfers every other week
    done on the dayOfWeek starting at 0 for Monday
    and increasing at APR daily compounded.
    You can skip to the next week first by using weekOffset of 1.
    """
    dayOfWeek: int = 0  # 0 indicates Monday
    weekOffset: int = 0  # From first week of year
    APR: APR = APR(0.0)

    def check(self):
        """ Check that all values are valid. """
        if not (0 <= self.dayOfWeek <= 6):
            raise ValueError(f"dayOfWeek should be between 0 (Monday) and 6 (Sunday). Got {self.dayOfWeek}")
        if not self.weekOffset in (0, 1):
            raise ValueError(f"weekOffset should be 0 or 1. Got {self.weekOffset}")


@dataclass()
class Monthly(Transfer):
    """
    Used to indicate monthly transfers done on the dayOfMonth
    and increasing at APR daily compounded.
    """
    dayOfMonth: int = 1  # Must be between 1 and 28 for leap years, later I'll add negatives to indicate "from end of month"
    APR: APR = APR(0)

    def check(self):
        """ Check that all values are valid. """
        if not (1 <= self.dayOfMonth <= 28):
            raise ValueError(f"dayOfMonth needs to be between 1 and 28. Got {self.dayOfMonth}")


# TODO: To Be Implemented
@dataclass()
class Yearly(Transfer):
    """
    Used to indicate yearly transfers done
    on the dayOfMonth of month and increasing at APR.
    """
    month: int = 1
    dayOfMonth: int = 1
    APR: APR = APR(0)

    def check(self):
        """ Check that all values are valid. """
        if not (1 <= self.month <= 12):
            raise ValueError(f"month needs to be between 1 and 12. Got {self.month}")
        if not (1 <= self.dayOfMonth <= 28):
            raise ValueError(f"dayOfMonth needs to be between 1 and 28. Got {self.dayOfMonth}")


# TODO: Implement
@dataclass()
class NYearly(Transfer):
    """
    Used to indicate every n years a transfer done
    on the dayOfMonth of month and increasing at APR.
    """
    nyears: int = 1
    month: int = 1
    dayOfMonth: int = 1
    firstYear: int = 1997
    APR: APR = APR(0)

    def check(self):
        """ Check that all values are valid. """
        if not (self.nyears >= 1):
            raise ValueError(f"nyears needs to be greater than or equal to 1. Got {self.nyears}")

