from datetime import datetime
from dataclasses import dataclass
from typing import List, Callable, Optional


@dataclass()
class Account:
    """
    An account like a bank account, or an asset,
    which can change over time with an APR,
    or be transfered to and from.
    """
    name: str
    amount: float
    APR: float
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
    to_account: str
    from_account: Optional[str] = None

    def check(self):
        """ Used to check the values are valid. """
        raise NotImplementedError()


@dataclass()
class Plan:
    accounts: List[Account]
    transfers: List[Transfer]


@dataclass()
class Bridge:
    trigger_date: datetime
    generate_plan: Callable[[Plan], Plan]

    def __call__(self, oldPlan: Plan):
        return self.generate_plan(oldPlan)


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
    APR: float = 0.0  # These are compounded daily


@dataclass()
class Weekly(Transfer):
    """
    Used to indicate transfers every week
    done on the dayOfWeek starting at 0 for Monday
    and increasing at APR daily compounded.
    """
    dayOfWeek: int = 0  # From Monday
    APR: float = 0.0

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
    APR: float = 0.0

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
    APR: float = 0.0

    def check(self):
        """ Check that all values are valid. """
        if not (1 <= self.dayOfMonth <= 28):
            raise ValueError(f"dayOfMonth needs to be between 1 and 28. Got {self.dayOfMonth}")


@dataclass()
class Yearly(Transfer):
    """
    Used to indicate yearly transfers done
    on the dayOfMonth of month and increasing at APR daily compounded.
    """
    month: int = 1
    dayOfMonth: int = 1
    APR: float = 0.0

    def check(self):
        """ Check that all values are valid. """
        if not (1 <= self.month <= 12):
            raise ValueError(f"month needs to be between 1 and 12. Got {self.month}")
        if not (1 <= self.dayOfMonth <= 28):
            raise ValueError(f"dayOfMonth needs to be between 1 and 28. Got {self.dayOfMonth}")


