from typing import List

import pandas as pd

from mql5_python.commons import MQL5Order, TradingSignals, TimeBarContent


class OutputWriter:
    def __init__(self, target_folder):
        self.date_lst = []
        self.close_lst = []
        self.signal_lst = []
        self.prev_signal_lst = []
        self.action_lst = []
        self.target_folder = target_folder

    def save_csv(
        self,
        contents: List[TimeBarContent],
        dframe,
        signal: TradingSignals,
        prev_signal: TradingSignals,
        predict_result: MQL5Order,
    ):
        date = contents[-1].datetime
        close = dframe["close"].iloc[-1]
        self.date_lst.append(date)
        self.close_lst.append(close)
        self.signal_lst.append(signal.value)
        self.prev_signal_lst.append(prev_signal.value)
        self.action_lst.append(predict_result.action.value)

    def output_csv(self):
        output_lst = [
            self.date_lst,
            self.close_lst,
            self.signal_lst,
            self.prev_signal_lst,
            self.action_lst,
        ]
        df_output = pd.DataFrame(output_lst).transpose()
        df_output.columns = ["date", "close_price", "signal", "prev_signal", "action"]
        print("-- df_output\n", df_output)
        df_output.to_csv(f"{self.target_folder}/output.csv", index=False)
        print("wrote output")
