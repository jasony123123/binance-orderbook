import asyncio
import websockets
import time
import json
import requests
import logging
import sys
import argparse


async def stream_orderbook(symbol='BNBBTC', record_freq=1, niter=30, depth=2):
    logging.basicConfig(stream=sys.stderr)
    logging.getLogger().setLevel(logging.INFO)
    logging.info(f"called: stream_orderbook(symbol={symbol}, record_freq={record_freq}, niter={niter}, depth={depth})")

    # connect to websocket
    async with websockets.connect(f"wss://stream.binance.com:9443/ws/{symbol.lower()}@depth@100ms") as websocket:
        bids: dict = None
        asks: dict = None
        snapshot_lastUpdateId: int = None
        prev_u = None

        # read from websocket
        # TODO: this code is sort of blocking (read-update's serially) ... concurrency would be better
        for i in range(niter):
            upd = await websocket.recv()
            upd = json.loads(upd)
            
            # initialize orderbook AFTER starting to read ... so nothing is missed
            if snapshot_lastUpdateId == None:
                snapshot = requests.get(f"https://api.binance.com/api/v3/depth?symbol={symbol.upper()}&limit={depth}").json()
                snapshot_lastUpdateId = snapshot['lastUpdateId']
                bids, asks = dict(snapshot['bids']), dict(snapshot['asks'])
                logging.info(f"Snapshot captured, update id ({snapshot_lastUpdateId})")
            
            # only update with non-already applied updates
            if upd['u'] >= snapshot_lastUpdateId + 1:
                # make sure updates follow one after the other
                if (upd['U'] <= snapshot_lastUpdateId+1 and prev_u == None) or (prev_u != None and upd['U'] == prev_u+1):
                    logging.info(f"iter({i}), UPDATE, U({upd['U']}, u({upd['u']})")
                    prev_u = upd['u']
                    for side, s in [(bids, 'b'), (asks, 'a')]:
                        # update each side, removing levels with quantity 0
                        for k,v in upd[s]:
                            if float(v) <= 1e-9 and k in side:
                                side.pop(k)
                        side.update(dict([(k,v) for k,v in upd[s] if float(v) >= 1e-9]))
                    if (i % record_freq) == 0:
                        # periodically print to stdout the entire orderbook
                        # TODO faster, non-blocking writes
                        print(json.dumps({'time': time.time(), 'bids': bids, 'asks': asks}, sort_keys=True, indent=2))
                else:
                    # TODO: better error handling
                    logging.error(f"iter({i}), BAD_PACKET, U({upd['U']}, u({upd['u']})")
            else:
                logging.info(f"iter({i}), STALE_PACKET, U({upd['U']}, u({upd['u']})")


if __name__ == "__main__":
    # TODO: more helpful documentation
    parser = argparse.ArgumentParser()
    parser.add_argument("symbol", type=str)
    parser.add_argument("freq", type=int)
    parser.add_argument("niter", type=int)
    parser.add_argument("depth", type=int)
    args = parser.parse_args()
    asyncio.run(stream_orderbook(args.symbol, args.freq, args.niter, args.depth))