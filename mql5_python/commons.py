import dataclasses

from enum import Enum
import datetime
import pandas as pd


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


class MQL5OrderTypes(Enum):
    Buy = "ORDER_TYPE_BUY"
    Modify = "POSITION_MODIFY"
    Close = "POSITION_CLOSE_SYMBOL"
    Sell = "ORDER_TYPE_SELL"
    Skip = "skip"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value


@dataclasses.dataclass
class MQL5Order:
    action: MQL5OrderTypes
    takeprofit: float = None
    stoploss: float = None

    def as_dict(self):
        return {
            "action": self.action.value,
            "takeprofit": self.takeprofit,
            "stoploss": self.stoploss,
        }


@dataclasses.dataclass
class DecisionMakerOutput:
    mql5_action: MQL5Order
    signal: TradingSignals
    prev_signal: TradingSignals
    df: pd.DataFrame
