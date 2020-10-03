from datetime import datetime
from dataclasses import dataclass
from typing import List, Callable, Optional


@dataclass()
class Account:
    name: str
    dollars: float
    APR: float
    created_on: datetime


@dataclass()
class Transfer:
    name: str
    amount: float
    to_account: str
    from_account: Optional[str] = None


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
    date: datetime = datetime.now()


@dataclass()
class Daily(Transfer):
    APR: float = 0.0


@dataclass()
class Weekly(Transfer):
    dayOfWeek: int = 0  # From Monday
    APR: float = 0.0


@dataclass()
class BiWeekly(Transfer):
    dayOfWeek: int = 0
    weekOffset: int = 0  # From first week of year
    APR: float = 0.0


@dataclass()
class Monthly(Transfer):
    dayOfMonth: int = 1
    APR: float = 0.0


@dataclass()
class Yearly(Transfer):
    month: int = 1
    dayOfMonth: int = 0
    APR: float = 0.0

