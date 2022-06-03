import abc
import pandas as pd


class AbstractStrategy(abc.ABC):
    def run(self, df: pd.DataFrame):
        raise NotImplementedError()
