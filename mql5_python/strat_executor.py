from typing import List

from datetime import datetime
import time
import os
import copy, sys
import pandas as pd
import numpy as np
import talib
import json

from mql5_python.commons import TimeBarContent, MQL5Order
from mql5_python.decision_maker import DecisionMaker
from mql5_python.output_writer import OutputWriter
import logging

logger = logging.getLogger(__name__)


class StratExecutor:
    """
    Watch the file `time_close_csv_test.csv` for new time bars, trigger the strategy to get signals,
    and write the output to `action_test.txt`
    """

    def __init__(self, trading_algrithm: DecisionMaker, input_file: str):
        self.trading_algrithm = trading_algrithm
        self.input_file = input_file
        self.target_folder = os.path.dirname(input_file)

    def write_strategies(self, data: MQL5Order):
        logger.info(f"write strategy output {data.as_dict()}")
        with open(f"{self.target_folder}/action_test.txt", "w") as outfile:
            json.dump(data.as_dict(), outfile)

    def save2csv(
        self,
        output_save,
        predict_result: MQL5Order,
        contents: List[TimeBarContent],
        signal,
        prev_signal,
        df,
    ):
        print("--- calling save2csv")
        output_save.save_csv(contents, df, signal, prev_signal, predict_result)
        print("-- called save2csv")

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
            # contents[i][0] = datetime.strptime(contents[i][0], "%Y.%m.%d %H:%M:%S")
            # contents[i][1] = float(contents[i][1])  # open
            # contents[i][2] = float(contents[i][2])  # high
            # contents[i][3] = float(contents[i][3])  # low
            # contents[i][4] = float(contents[i][4])  # close
            # contents[i][5] = int(contents[i][5])  # tick value
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
        output_save = OutputWriter(target_folder=self.target_folder)

        if os.path.isfile(filename) and os.stat(filename).st_size != 0:
            logger.info("File exist and not empty")
            # watch the file for multiple runs
            while True:
                pre_Timebar = 0
                check_point = 0
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
                                output_save.output_csv()
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
                                    self.write_strategies(predict_result)
                                    # self.cleanFile(filename)

                                    self.save2csv(
                                        output_save,
                                        predict_result,
                                        contents,
                                        signal,
                                        prev_signal,
                                        df,
                                    )

                                    check_point += 1

                                    if check_point % 50 == 0:
                                        output_save.output_csv()

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
