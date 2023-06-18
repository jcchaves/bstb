import asyncio
from binance import BinanceSocketManager
from binance.exceptions import BinanceAPIException
import json
import logging

logger = logging.getLogger(__name__)


class PriceMovementMonitor:
    def __init__(self, bncClient, loop):
        self._bncClient = bncClient
        self._loop = loop
        self.submit_async(self.process(), loop)

    def submit_async(self, awaitable, loop):
        loop.create_task(awaitable)

    def process_message(self, msg):
        if "e" in msg and msg["e"] == "error":
            # close and restart the socket
            logger.error("Websocket connection lost, attempting reconnection...")
        else:
            logger.info(msg)

    async def process(self):
        logger.info("Processing prices....")
        bm = BinanceSocketManager(self._bncClient, user_timeout=10, loop=self._loop)
        tickersSock = bm.all_mark_price_socket()
        # then start receiving messages
        try:
            async with tickersSock as tickers:
                while True:
                    msg = await tickers.recv()
                    self.process_message(msg)
        except BinanceAPIException as e:
            print(e)
