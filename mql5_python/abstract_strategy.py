import abc
import pandas as pd


class AbstractStrategy(abc.ABC):
    def run(self, df: pd.DataFrame):
        self.df = df
        self.close = df["close"]
