# Setup

Install the conda enviornment provided (`condaenv`) and activate it.

# Run

`python3 script.py {symbol} {frequency_of_snapshots} {number_of_updates_to_run_for} {levels_in_orderbook} > output`

E.g. `python3 script.py BNBBTC 20 250 1000 > output`

Output stores the orderbook as a series of JSON style objects. An example of the format is provided in `output`.