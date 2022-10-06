# Take-home task

## Task description

Use the Binance Spot API to implement a client that listens to the "Diff. Depth Stream" WebSocket market stream with 100ms update frequency (a.k.a. `<symbol>@depth@100ms>`) to reconstruct an L2 (market-by-price) orderbook locally and save it in some format for future analysis.

- note that you will have to output full orderbook snapshots, which must be correct, and not simply deltas or something else that requires further reconstruction
- the orderbook snapshots must be L2/market-by-price, i.e. show the sizes at each price level
- to reduce the volume written, you can output snapshots only once every N orderbook updates, where N is an argument supplied to the program
- you may choose/design the serialisation and storage format; ideally it should be easy to read/parse, but you do not necessarily need to write a parser for it
- it's a bonus if your client attempts to handle message gaps/disconnections/network errors/API outages in a thoughtful way

## Guidelines

- an adequate solution can take 1-3 hours depending on experience and luck, please don't spend more than 3 hours on the project
- if you're running low on time, make something with reduced scope that still runs and does something useful
- thoughtful, clean and readable code is better than aiming for feature completeness or best performance
- if you are aware of any major problems/weaknesses, document them with concise comments in the code
- do not feel the need to optimise at the expense of simplicity, if you have ideas for important optimisations to be done in the future, you can describe them with comments in the code
- if anything is ambiguous or open-ended, interpret it in light of what you think would be most useful in practice
- you may use Python (or a different language if you think it's more productive, but recommend to ask first)
- present the code in a way that makes it easy for others to run, including a readme with instructions mentioning how to compile/run it, dependencies, etc.
