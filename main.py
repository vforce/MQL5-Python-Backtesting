# import your trading strategy here
# from sma_ema import SimpleMAExponentialMA
from mql5_python.strat_executor import StratExecutor
from mql5_python.decision_maker import DecisionMaker

# from trading_strategies.adx_crossover import AdxCrossover
# from trading_strategies.aroon_adx import AroonAdx
# from trading_strategies.sma_mi import SMAMI
# from trading_strategies.stochastic_oscillator_no_exit import StochasticOscillatorNoExit
# from trading_strategies.aroon_indicator import AroonIndicator
# from trading_strategies.awesome_saucer import AwesomeOscillatorSaucer
# from trading_strategies.blade_runner import BladeRunner
# from trading_strategies.bollingerbands_rsi_2 import BollingerBandsAndRSI2
# from trading_strategies.cci_macd_psar import CciMacdPsar
# from trading_strategies.dpo_candlestick import DpoCandlestick
# from trading_strategies.elder_ray_sma import ElderRaySma
# from trading_strategies.ema_3 import ThreeEma
# from trading_strategies.ema_crossover_alternative import EMACrossover
# from trading_strategies.ema_crossover_macd import EMACrossoverMACD
# from trading_strategies.ema_crossover_rsi_alternative import EMACrossoverRSI
# from trading_strategies.ema_crossover_rsi import EMACrossoverRSI
# from trading_strategies.ema_crossover import EMACrossover
# from trading_strategies.williams_stochastic import WilliamsStochastic
# from trading_strategies.macd_crossover import MACDCrossover
# from trading_strategies.macd_rsi_sma import MacdRsiSma
# from trading_strategies.macd_stochastic_crossover import MACDStochasticCrossover
# from trading_strategies.rsi_2 import Rsi2
# from trading_strategies.rsi_80_20 import Rsi8020
# from trading_strategies.triple_bollingerbands import TripleBollingerBands
# from trading_strategies.trix_ema import TrixEma
# from trading_strategies.trix_rsi import TrixRsi
# from trading_strategies.vortex_crossover import VortexCrossover
# from trading_strategies.vortex_sma import VortexSma
# from trading_strategies.williams_r_sma import WilliamsIndicator
# from trading_strategies.williams_rsi import WilliamsRsi
# from trading_strategies.commodity_channel_index import CommodityChannelIndex
# rom trading_strategies.donchian_breakout import DonchianBreakout

# optional import, only use for demo
from datetime import datetime

# using pip install panda if missing modules pandas
import pandas as pd

# non-optional import:
from mql5_python.strategies.simple_ma_ema import SimpleMAExponentialMA
import logging

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    file_path = "/Users/kdang/Library/Application Support/MetaTrader 5/Bottles/metatrader5/drive_c/Program Files/MetaTrader 5/Tester/Agent-127.0.0.1-3000/MQL5/Files/time_close_csv_test.csv"
    ai = DecisionMaker(SimpleMAExponentialMA())
    executor = StratExecutor(ai, file_path)
    executor.run()
