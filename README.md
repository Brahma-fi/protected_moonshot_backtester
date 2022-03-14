# protected_moonshot_backtester

## Introduction

This repository contains python scripts that are used by [Brahma Finance](https://brahma.fi/) to simulate the performance of the Protected Moonshot DegenVault. The repo is structured as follows:

[data/](https://github.com/Brahma-fi/protected_moonshot_backtester/tree/master/data) folder contains the csv files related to ETHUSD price data from FTX and Chainlink rounds.

In terms of the python files:

1. [utils.py](https://github.com/Brahma-fi/protected_moonshot_backtester/blob/master/utils.py) contains all the functions used to process the raw data.
2. [trading_utils.py](https://github.com/Brahma-fi/protected_moonshot_backtester/blob/master/trading_utils.py) contains functions to backtest the enhanced strategy
3. [trading_utils_simple.py](https://github.com/Brahma-fi/protected_moonshot_backtester/blob/master/trading_utils_simple.py) contains functions to backtest the simple strategy


In order to run the backtest for the strategy use the two notebooks:

- [moonshot_simple.ipynb](https://github.com/Brahma-fi/protected_moonshot_backtester/blob/master/moonshots_simple.ipynb) runs the analysis for the simple strategy explained in the [Protected Moonshot Blog Post](https://blog.brahma.fi/launching-protected-moonshot-degenvault/). 
- [moonshot_enhanced.ipynb](https://github.com/Brahma-fi/protected_moonshot_backtester/blob/master/moonshots_enhanced.ipynb) runs the analysis for the enhanced strategy explained in the [Protected Moonshot Blog Post](https://blog.brahma.fi/launching-protected-moonshot-degenvault/)

 
