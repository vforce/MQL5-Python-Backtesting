from typing import Tuple
from trading_strategies.abstract_strategy import AbstractStrategy, TradingSignals
import pandas as pd


class StratMartingale(AbstractStrategy):
    def __init__(self, csv_file_path: str):
        super().__init__(csv_file_path)

    def run(self) -> Tuple[TradingSignals, pd.DataFrame]:
        return TradingSignals.Noop, self.df

