import abc
import pandas as pd


class AbstractStrategy(abc.ABC):
    def run(self):
        raise NotImplementedError()

    def init_df(self, df: pd.DataFrame):
        self.df = df
        self.close = df["close"]
