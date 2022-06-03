from typing import Tuple

import abc
import pandas as pd

from mql5_python.commons import TradingSignals


class AbstractStrategy(abc.ABC):
    def run(self) -> Tuple[TradingSignals, pd.DataFrame]:
        raise NotImplementedError()

    def init_df(self, df: pd.DataFrame):
        self.df = df
        self.close = df["close"]
