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

    async with websockets.connect(f"wss://stream.binance.com:9443/ws/{symbol.lower()}@depth@100ms") as websocket:
        bids: dict = None
        asks: dict = None
        snapshot_lastUpdateId: int = None
        prev_u = None

        for i in range(niter):
            upd = await websocket.recv()
            upd = json.loads(upd)
            
            if snapshot_lastUpdateId == None:
                snapshot = requests.get(f"https://api.binance.com/api/v3/depth?symbol={symbol.upper()}&limit={depth}").json()
                snapshot_lastUpdateId = snapshot['lastUpdateId']
                bids, asks = dict(snapshot['bids']), dict(snapshot['asks'])
                logging.info(f"Snapshot captured, update id ({snapshot_lastUpdateId})")
            
            if upd['u'] >= snapshot_lastUpdateId + 1:
                if (upd['U'] <= snapshot_lastUpdateId+1 and prev_u == None) or (prev_u != None and upd['U'] == prev_u+1):
                    logging.info(f"iter({i}), UPDATE, U({upd['U']}, u({upd['u']})")
                    prev_u = upd['u']
                    for side, s in [(bids, 'b'), (asks, 'a')]:
                        logging.info(f"{s} remove 0s {[(k, side.pop(k), v) for k,v in upd[s] if float(v) <= 1e-9 and k in side]}")
                        side.update(dict([(k,v) for k,v in upd[s] if float(v) >= 1e-9]))
                    if (i % record_freq) == 0:
                        print(json.dumps({'time': time.time(), 'bids': bids, 'asks': asks}, sort_keys=True, indent=2))
                else:
                    logging.error(f"iter({i}), BAD_PACKET, U({upd['U']}, u({upd['u']})")
            else:
                logging.info(f"iter({i}), STALE_PACKET, U({upd['U']}, u({upd['u']})")


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("symbol", type=str)
    parser.add_argument("freq", type=int)
    parser.add_argument("niter", type=int)
    parser.add_argument("depth", type=int)
    args = parser.parse_args()
    asyncio.run(stream_orderbook(args.symbol, args.freq, args.niter, args.depth))