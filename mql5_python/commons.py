import dataclasses

from enum import Enum
import datetime


class TradingSignals(Enum):
    Buy = 1
    Sell = -1
    Hold = 0


@dataclasses.dataclass
class TimeBarContent:
    datetime: datetime
    current_status: str
    open: float
    high: float
    low: float
    close: float
    tick_value: int
