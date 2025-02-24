from dataclasses import asdict

from typing import List

import pandas as pd

from mql5_python.abstract_strategy import AbstractStrategy
from mql5_python.commons import (
    TradingSignals,
    TimeBarContent,
    DecisionMakerOutput,
    MQL5Order,
    MQL5OrderTypes,
)
import logging

logger = logging.getLogger(__name__)


class DecisionMaker:
    def __init__(
        self,
        strategy: AbstractStrategy,
        take_profit: float = 0.0050,
        stop_loss: float = -0.0020,
    ):
        self.prev_signal = 0  # what the previous signal was was e.g. 1 for buy , -1 for sell, 0 for hold
        self.prev_traded_price = 0  # this is the previously traded price for an exisiting position (entry price)
        self.curr_stop_loss = 0  # current stop loss
        self.curr_take_profit = 0  # current take profit
        self.strategy = strategy
        self.take_profit = take_profit
        self.stop_loss = stop_loss

    # for the last candle (data) of the given currency (symbol), provided its historical data(history) predict whether to buy or sell
    def predict(self, history: List[TimeBarContent]) -> DecisionMakerOutput:

        # convert history to pandas dataframe
        history_dataframe = pd.DataFrame(
            [asdict(h) for h in history],
        )
        # print("history dataframe", history_dataframe.head())

        # extract meaningful values
        prev_close_price = history[-2].close
        curr_close_price = history[-1].close
        curr_high_price = history[-1].high
        curr_low_price = history[-1].low
        date = history[-1].datetime

        # adjust TP/SL values here, remember to x100 if testing on JPY currency
        # take_profit = 0.0200
        take_profit = self.take_profit
        # stop_loss = -0.0250
        stop_loss = self.stop_loss

        logger.info("-----")
        logger.info(f"date: {date}, close = {curr_close_price}")
        self.strategy.init_df(history_dataframe)
        signal, df = self.strategy.run()

        # first check if stop loss/take profit has been triggered

        if self.prev_signal == TradingSignals.Buy and (
            (self.curr_take_profit != 0 and curr_high_price >= self.curr_take_profit)
            or (self.curr_stop_loss != 0 and curr_low_price <= self.curr_stop_loss)
        ):
            self.prev_signal = (
                TradingSignals.Hold
            )  # since the sl/tp was triggered, we reset position

        if self.prev_signal == TradingSignals.Sell and (
            (self.curr_take_profit != 0 and curr_low_price <= self.curr_take_profit)
            or (self.curr_stop_loss != 0 and curr_high_price >= self.curr_stop_loss)
        ):
            self.prev_signal = (
                TradingSignals.Hold
            )  # since the sl/tp was triggered, we reset position

        logger.info(f"signal: {signal}, prev signal = {self.prev_signal}")
        # then we look at the signal returned
        if signal == TradingSignals.Buy:

            # if previous signal was a sell, close off the position
            if self.prev_signal == TradingSignals.Sell:
                # make previous signal 0 as we don't have an active position
                self.prev_signal = TradingSignals.Hold
                return DecisionMakerOutput(
                    mql5_action=MQL5Order(
                        action=MQL5OrderTypes.Close,
                    ),
                    signal=signal,
                    prev_signal=self.prev_signal,
                    df=df,
                )  # close

            # if previous signal was 0, there was no active position, open a long position
            if self.prev_signal == TradingSignals.Hold:
                self.prev_signal = signal
                self.prev_traded_price = curr_close_price
                self.curr_stop_loss = curr_close_price + stop_loss
                self.curr_take_profit = curr_close_price + take_profit
                return DecisionMakerOutput(
                    mql5_action=MQL5Order(
                        action=MQL5OrderTypes.Buy,
                        takeprofit=curr_close_price + take_profit,
                        stoploss=curr_close_price + stop_loss,
                    ),
                    signal=signal,
                    prev_signal=self.prev_signal,
                    df=df,
                )

            # otherwise, the previous signal was another buy (pre_signal == 1)
            # as a result, we do not buy again, instead we adjust the SL/TP
            else:
                self.prev_signal = signal

                # if its a higher buy signal we increase our TP/SL by the same spread as the original
                if (
                    curr_close_price > prev_close_price
                    and curr_close_price > self.prev_traded_price
                ):
                    self.curr_stop_loss = curr_close_price + stop_loss
                    self.curr_take_profit = curr_close_price + take_profit
                    return DecisionMakerOutput(
                        mql5_action=MQL5Order(
                            action=MQL5OrderTypes.Modify,
                            takeprofit=curr_close_price + take_profit,
                            stoploss=curr_close_price + stop_loss,
                        ),
                        signal=signal,
                        prev_signal=self.prev_signal,
                        df=df,
                    )

                # if its a lower buy signal we dont change our take profit or stop loss
                else:
                    return DecisionMakerOutput(
                        mql5_action=MQL5Order(action=MQL5OrderTypes.Skip),
                        signal=signal,
                        prev_signal=self.prev_signal,
                        df=df,
                    )

        if signal == TradingSignals.Sell:

            # if previous signal was a buy, close off the position
            if self.prev_signal == TradingSignals.Buy:
                # make previous signal 0 as we don't have an active position
                self.prev_signal = TradingSignals.Hold
                return DecisionMakerOutput(
                    mql5_action=MQL5Order(
                        action=MQL5OrderTypes.Close,
                    ),
                    signal=signal,
                    prev_signal=self.prev_signal,
                    df=df,
                )  # close

            # if previous signal was 0, there was no active position, open a short position
            if self.prev_signal == TradingSignals.Hold:
                self.prev_signal = signal
                self.prev_traded_price = curr_close_price
                self.curr_stop_loss = curr_close_price - stop_loss
                self.curr_take_profit = curr_close_price - take_profit
                return DecisionMakerOutput(
                    mql5_action=MQL5Order(
                        action=MQL5OrderTypes.Sell,
                        takeprofit=curr_close_price - self.curr_take_profit,
                        stoploss=curr_close_price - self.curr_stop_loss,
                    ),
                    signal=signal,
                    prev_signal=self.prev_signal,
                    df=df,
                )

            # otherwise, the previous signal was another sell
            # as a result, we do not sell again, instead we adjust the SL/TP
            else:
                # if its a lower sell signal we increase our take profit and increase our stop loss by the same spread as the original
                if (
                    curr_close_price < prev_close_price
                    and curr_close_price < self.prev_traded_price
                ):
                    self.curr_stop_loss = curr_close_price - stop_loss
                    self.curr_take_profit = curr_close_price - take_profit
                    return DecisionMakerOutput(
                        mql5_action=MQL5Order(
                            action=MQL5OrderTypes.Modify,
                            takeprofit=curr_close_price - take_profit,
                            stoploss=curr_close_price - stop_loss,
                        ),
                        signal=signal,
                        prev_signal=self.prev_signal,
                        df=df,
                    )

                # if its a lower sell signal we dont change our take profit or stop loss aka do nothing
                else:
                    return DecisionMakerOutput(
                        mql5_action=MQL5Order(action=MQL5OrderTypes.Skip),
                        signal=signal,
                        prev_signal=self.prev_signal,
                        df=df,
                    )

        if signal == TradingSignals.Hold:
            return DecisionMakerOutput(
                mql5_action=MQL5Order(action=MQL5OrderTypes.Skip),
                signal=signal,
                prev_signal=self.prev_signal,
                df=df,
            )
