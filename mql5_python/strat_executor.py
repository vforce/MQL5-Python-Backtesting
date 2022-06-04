from typing import List

from datetime import datetime
import time
import os
import copy, sys
import pandas as pd
import numpy as np
import talib
import json

from mql5_python.commons import TimeBarContent, MQL5Order, TradingSignals
from mql5_python.decision_maker import DecisionMaker
import logging

logger = logging.getLogger(__name__)


class StratExecutor:
    """
    Watch the file `time_close_csv_test.csv` for new time bars, trigger the strategy to get signals,
    and write the output to `action_test.txt`
    """

    class __OutputWriter:
        """
        Helper class to help write output to folder. Not supposed to be used elsewhere, therefore
        putting it as a private class
        """

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
            df_output.columns = [
                "date",
                "close_price",
                "signal",
                "prev_signal",
                "action",
            ]
            df_output.to_csv(f"{self.target_folder}/output.csv", index=False)

        def write_strategies(self, data: MQL5Order):
            logger.info(f"write strategy output {data.as_dict()}")
            with open(f"{self.target_folder}/action_test.txt", "w") as outfile:
                json.dump(data.as_dict(), outfile)

    def __init__(self, trading_algrithm: DecisionMaker, input_file: str):
        self.trading_algrithm = trading_algrithm
        self.input_file = input_file
        self.target_folder = os.path.dirname(input_file)

    def cleanFile(self, filename):
        del_f = open(filename, "w")
        del_f.close()

    def convert_csv_file_to_history(self, filename: str) -> List[TimeBarContent]:
        """
        Read file and convert to a list of TimeBarContent.
        pd.read_csv() is not working because of special characters in the input file
        :return:
        """

        with open(filename, encoding="utf-16") as f:
            contents = f.read()
        # you may also want to remove whitespace characters like `\n` at the end of each line
        contents = contents.splitlines()
        contents = [x.split("\t") for x in contents]
        results = []
        for i in range(len(contents)):
            results.append(
                TimeBarContent(
                    datetime=datetime.strptime(contents[i][0], "%Y.%m.%d %H:%M:%S"),
                    open=float(contents[i][1]),  # open
                    high=float(contents[i][2]),  # high
                    low=float(contents[i][3]),  # low
                    close=float(contents[i][4]),  # close
                    tick_value=int(contents[i][5]),  # tick value
                    current_status=contents[i][6],
                )
            )

        return results

    def run(self):
        """
        Watch the file `time_close_csv_test.csv` for new time bars, trigger the strategy to get signals,
        To stop the server, press Ctrl+C
        :return:
        """
        filename = self.input_file

        if os.path.isfile(filename) and os.stat(filename).st_size != 0:
            logger.info("File exist and not empty")
            # watch the file for multiple runs
            while True:
                pre_Timebar = 0
                check_point = 0
                output_writer = self.__OutputWriter(target_folder=self.target_folder)
                while True:
                    if os.stat(filename).st_size != 0:
                        try:
                            contents: List[
                                TimeBarContent
                            ] = self.convert_csv_file_to_history(filename)
                            newTimebar = contents[-1].datetime
                            curr_position = contents[-1].current_status
                            curr_close_price = contents[-1].close
                            if curr_position == "Ending":
                                # print(">>>------------------------<<<")
                                output_writer.output_csv()
                                # print(">>> Server Stop <<<")
                                break

                            else:
                                if pre_Timebar != newTimebar:
                                    pre_Timebar = copy.deepcopy(newTimebar)

                                    logger.debug(
                                        f"Timebar: {pre_Timebar}, close price = {curr_close_price}, cur position = {curr_position}"
                                    )

                                    # code from example2.py, send the data to the main_DecisionMaker.py

                                    decision_maker_output = (
                                        self.trading_algrithm.predict(contents)
                                    )
                                    predict_result = decision_maker_output.mql5_action
                                    signal = decision_maker_output.signal
                                    prev_signal = decision_maker_output.prev_signal
                                    df = decision_maker_output.df

                                    if not isinstance(predict_result, MQL5Order):
                                        raise ValueError(
                                            f"Predition result must be of type {MQL5Order.__class__.__name__}"
                                        )
                                    logger.info(f"predict_result\t {predict_result}")

                                    # write the result to txt or csv
                                    output_writer.write_strategies(predict_result)

                                    # self.cleanFile(filename)

                                    output_writer.save_csv(
                                        predict_result=predict_result,
                                        contents=contents,
                                        signal=signal,
                                        prev_signal=prev_signal,
                                        dframe=df,
                                    )

                                    check_point += 1

                                    if check_point % 50 == 0:
                                        output_writer.output_csv()

                                else:
                                    time.sleep(0.003)

                        except:
                            continue

                    else:
                        # print("File is empty")
                        time.sleep(0.001)
                time.sleep(0.1)
        else:
            logger.error("File not exist")
