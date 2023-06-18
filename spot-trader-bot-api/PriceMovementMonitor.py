import asyncio
from binance import BinanceSocketManager
from binance.exceptions import BinanceAPIException
import json
import logging

logger = logging.getLogger(__name__)


class PriceMovementMonitor:
    def __init__(self, bncClient, mainLoop, loop, alertNotifier):
        self._bncClient = bncClient
        self._mainLoop = mainLoop
        self._loop = loop
        self._alertNotifier = alertNotifier
        self.submit_async(self.process(), loop)

    def submit_async(self, awaitable, loop):
        loop.create_task(awaitable)

    async def process_message(self, msg: str):
        if "e" in msg and msg["e"] == "error":
            # close and restart the socket
            logger.error("Websocket connection lost, attempting reconnection...")
        else:
            logger.info(f"Verify conditions...")
            longer_period_condition_met = False
            shorter_period_condition_met = False

            if longer_period_condition_met and shorter_period_condition_met:
                # Send alert for shorter period
                pass
            elif longer_period_condition_met and not shorter_period_condition_met:
                # Send alert for longer period
                pass
            elif not longer_period_condition_met and shorter_period_condition_met:
                # Send alert for shorter period
                pass
            else:
                # Do not send any alert
                pass

            self._mainLoop.call_soon_threadsafe(
                self._alertNotifier.publish, json.dumps(msg)
            )

    async def process(self):
        logger.info("Processing prices....")
        bm = BinanceSocketManager(self._bncClient, user_timeout=10, loop=self._loop)
        tickersSock = bm.all_mark_price_socket()
        # then start receiving messages
        try:
            async with tickersSock as tickers:
                while True:
                    msg = await tickers.recv()
                    await self.process_message(msg)
        except BinanceAPIException as e:
            print(e)
