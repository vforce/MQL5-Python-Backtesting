# MQL5-Python-Backtesting

MQL5 based backtesting using python

# Instruction

- Get the path to MetaTrader5 folder. On Mac, it looks something like this. Let's call this ROOT_DIR

```
/Users/<username>/Library/Application Support/MetaTrader 5/Bottles/metatrader5/drive_c/Program Files/MetaTrader 5/MQL5/
```

- Copy the files in MQL5 folder into `ROOT_DIR/MQL5/Experts`
- On MT5, open the Strategy Tester interface. On tab `Settings`, select the expert `py_json_csv_0204.ex5`. Select the duration you want to test. Make sure to tick `visual mode with the display of charts....`. Click start to start an empty test for now.
- Make sure that in the folder `ROOT_DIR/Tester/Agent-.../MQL5/Files/`, there's a file name `time_close_csv_test.csv`. Once you have this file, you can start running the python file.
- Now run the `main_DecisionMaker.py` file
- Go back to the main window, press `Start` in the `Strategy Tester` tab to start back testing.

# OLD instruction

Trading strategies send the buy, sell or hold signal to MQL5
Based on the signal Metatrader 5 perform the trading

How to run the Strategies:

1. open main_decisionmaker.py and import the trading strategy which is intended to run
2. Update the strategy and the signal line
3. Start the backtesting in Metatrader 5
4. Copy the python files along with the strategy folder(trading_strategies) into Metatrader 5 testing/files folder
5. copy other python files - main_decisionmaker.py, output.py and actionWriter.py
6. run main_decisionmaker.py

Explained in this video https://www.youtube.com/watch?v=ovKgQdiQsHE&t=764s
