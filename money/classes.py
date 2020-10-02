from datetime import datetime
from dataclasses import dataclass
from typing import List, Callable, Optional


@dataclass(frozen=True)
class Account:
    name: str
    dollars: float
    APR: float
    created_on: datetime


@dataclass(frozen=True)
class Transfer:
    name: str
    amount: float
    to_account: str
    from_account: Optional[str] = None


@dataclass(frozen=True)
class Plan:
    accounts: List[Account]
    transfers: List[Transfer]


@dataclass(frozen=True)
class Bridge:
    trigger_date: datetime
    generate_plan: Callable[[Plan], Plan]

    def __call__(self, oldPlan: Plan):
        return self.generate_plan(oldPlan)


@dataclass(frozen=True)
class Once(Transfer):
    date: datetime = datetime.now()


@dataclass(frozen=True)
class Daily(Transfer):
    APR: float = 0.0


@dataclass(frozen=True)
class Weekly(Transfer):
    dayOfWeek: int = 0  # From Monday
    APR: float = 0.0


@dataclass(frozen=True)
class BiWeekly(Transfer):
    dayOfWeek: int = 0
    weekOffset: int = 0  # From first week of year
    APR: float = 0.0


@dataclass(frozen=True)
class Monthly(Transfer):
    dayOfMonth: int = 0
    APR: float = 0.0


@dataclass(frozen=True)
class Yearly(Transfer):
    month: int = 0
    dayOfMonth: int = 0
    APR: float = 0.0

