import asyncio
from binance import AsyncClient, BinanceSocketManager, Client
from binance.exceptions import BinanceAPIException
import json
import logging
from KLinesFetcher import KLinesFetcher

logger = logging.getLogger(__name__)


class PriceMovementMonitor:
    def __init__(
        self, mainLoop, loop, alertNotifier, leverageThreshold, accessKey, secretKey
    ):
        self._mainLoop = mainLoop
        self._loop = loop
        self._alertNotifier = alertNotifier
        self._leverageThreshold = leverageThreshold
        self._accessKey = accessKey
        self._secretKey = secretKey
        self._klines = {}
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

    async def leverageTickers(self, tickers):
        filteredTickers = []
        leverages = await self._bncClient.futures_leverage_bracket()
        leveragesMap = {}
        for leverage in leverages:
            leveragesMap[leverage["symbol"]] = {"brackets": leverage["brackets"]}
        for ticker in tickers:
            brackets = [
                bracket
                for bracket in leveragesMap[ticker]["brackets"]
                if bracket["initialLeverage"] >= self._leverageThreshold
            ]
            if len(brackets) > 0:
                filteredTickers.append(ticker)
        return filteredTickers

    async def process(self):
        try:
            self._bncClient = await AsyncClient.create(self._accessKey, self._secretKey)
            logger.debug("Fetch all tickers of interest...")
            tickers = await self._bncClient.futures_symbol_ticker()
            tickersOfInterest = [
                ticker["symbol"]
                for ticker in tickers
                if ticker["symbol"][-4:] != "USDT"
            ]

            filteredTickers = await self.leverageTickers(tickersOfInterest)

            logger.debug("Fetching last 15 minutes klines...")
            klinesFetcher = KLinesFetcher(
                self._bncClient,
                self._accessKey,
                self._secretKey,
            )
            await klinesFetcher.fetchAllTickersKLines(filteredTickers)
            logger.info("Showing last 15 minutes klines")
            print(klinesFetcher.getKLines())
            logger.info("Processing prices....")
            bm = BinanceSocketManager(self._bncClient, user_timeout=10, loop=self._loop)
            tickersSock = bm.all_mark_price_socket()
            # then start receiving messages
            async with tickersSock as tickers:
                while True:
                    msg = await tickers.recv()
                    await self.process_message(msg)
        except BinanceAPIException as e:
            print(e)
