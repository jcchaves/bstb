import asyncio
from datetime import datetime, timezone
from binance import AsyncClient, BinanceSocketManager, Client
from binance.exceptions import BinanceAPIException
import json
import logging

from KLine import KLine
from KLinesFetcher import KLinesFetcher

logger = logging.getLogger(__name__)


class PriceMovementMonitor:
    def __init__(
        self,
        mainLoop,
        loop,
        alertNotifier,
        leverageThreshold,
        longerPeriodPercentThreshold,
        shorterPeriodPercentThreshold,
        accessKey,
        secretKey,
    ):
        self._mainLoop = mainLoop
        self._loop = loop
        self._alertNotifier = alertNotifier
        self._leverageThreshold = leverageThreshold
        self._longerPeriodPercentThreshold = longerPeriodPercentThreshold
        self._shorterPeriodPercentThreshold = shorterPeriodPercentThreshold
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
            if "data" in msg:
                latestTickers = msg["data"]
                logger.debug("Update ticker klines...")
                for ticker in latestTickers:
                    logger.debug(f"Updating ticker '{ticker}' klines")
                    self.updateTickerKline(
                        ticker["s"],
                        ticker["E"] / 1000,
                        float(ticker["p"]),
                    )

                logger.info(f"Verify conditions...")
                for ticker in latestTickers:
                    longer_period_condition_met = False
                    shorter_period_condition_met = False
                    if ticker["s"] in self._klines:
                        tickerKlines = self._klines[ticker["s"]]
                        kline15MinsAgo = tickerKlines[0]
                        kline2MinsAgo = tickerKlines[len(tickerKlines) - 3]
                        latestKline = tickerKlines[len(tickerKlines) - 1]

                        percentDiff15mins = self.calculatePercentDiff(
                            kline15MinsAgo.getOpen(), latestKline.getClose()
                        )
                        longer_period_condition_met = (
                            abs(percentDiff15mins) > self._longerPeriodPercentThreshold
                        )
                        percentDiff2mins = self.calculatePercentDiff(
                            kline2MinsAgo.getOpen(), latestKline.getClose()
                        )
                        shorter_period_condition_met = (
                            abs(percentDiff2mins) > self._shorterPeriodPercentThreshold
                        )
                        logger.info(
                            f"\n\t{ticker['s']} current price: {ticker['p']}\n\t{ticker['s']} open price 15 mins ago:\t{kline15MinsAgo.getOpen()}\n\t{ticker['s']} open price 2 mins ago:\t{kline2MinsAgo.getOpen()}\n\t{ticker['s']} price % diff against 15 mins ago:\t{abs(percentDiff15mins)}%\n\t{ticker['s']} price % diff against 2 mins ago:\t{abs(percentDiff2mins)}%"
                        )
                        if longer_period_condition_met and shorter_period_condition_met:
                            # Send alert for shorter period
                            logger.info(
                                f"ALERT - Ticker {ticker} has changed more than {self._shorterPeriodPercentThreshold} in the last 2 minutes"
                            )
                        elif (
                            longer_period_condition_met
                            and not shorter_period_condition_met
                        ):
                            # Send alert for longer period
                            logger.info(
                                f"ALERT - Ticker {ticker['s']} has changed more than {self._longerPeriodPercentThreshold}% in the last 15 minutes"
                            )
                        elif (
                            not longer_period_condition_met
                            and shorter_period_condition_met
                        ):
                            # Send alert for shorter period
                            logger.info(
                                f"ALERT - Ticker {ticker['s']} has changed more than {self._shorterPeriodPercentThreshold}% in the last 2 minutes"
                            )
                        else:
                            # Do not send any alert
                            logger.debug(
                                f"No alert - Ticker {ticker['s']} has not changed more than {self._longerPeriodPercentThreshold}% in the last 15 minutes, or more than {self._shorterPeriodPercentThreshold}% in the last 2 minutes"
                            )

                        self._mainLoop.call_soon_threadsafe(
                            self._alertNotifier.publish, json.dumps(msg)
                        )
                    else:
                        logger.debug(f"No klines captured for symbol '{ticker['s']}'")

    def updateTickerKline(self, ticker, timestamp, latestPrice):
        if ticker in self._klines:
            tickerKlines = self._klines[ticker]
            currentTs = datetime.fromtimestamp(timestamp, tz=timezone.utc)
            currentMinuteTs = datetime(
                year=currentTs.year,
                month=currentTs.month,
                day=currentTs.day,
                hour=currentTs.hour,
                minute=currentTs.minute,
                tzinfo=timezone.utc,
            ).timestamp()
            # Check if current minute kline has the same timestamp as the latest kline open timestamp in memory
            latestTickerKline = tickerKlines[len(tickerKlines) - 1]
            logger.debug(f"Latest kline for ticker {ticker}: {latestTickerKline}")
            if latestTickerKline.getOpenTimestamp() != currentMinuteTs:
                # if not, remove the oldest kline, create a new kline and set open and close price to the same value, and add the new kline to the list of klines for the ticker
                currentMinuteKline = KLine(
                    ticker,
                    openTimestamp=currentMinuteTs,
                    closeTimestamp=currentMinuteTs + 59,
                    open=latestPrice,
                    close=latestPrice,
                )
                tickerKlines.pop(0)
                tickerKlines.append(currentMinuteKline)
            else:
                # if it is, update its close value to the latest symbol price
                curMinKline = tickerKlines.pop(len(tickerKlines) - 1)
                updatedCurMinKline = KLine(
                    curMinKline.getTicker(),
                    openTimestamp=curMinKline.getOpenTimestamp(),
                    closeTimestamp=curMinKline.getCloseTimestamp(),
                    open=curMinKline.getOpen(),
                    close=latestPrice,
                )
                tickerKlines.append(updatedCurMinKline)
            # Update klines for ticker
            self._klines[ticker] = tickerKlines
        else:
            logger.debug(f"No klines to update for ticker {ticker}")

    def calculatePercentDiff(self, initial, latest):
        return ((latest - initial) / initial) * 100

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

            tickers = [{"symbol": "BTCUSDT"}]

            tickersOfInterest = [
                ticker["symbol"]
                for ticker in tickers
                if ticker["symbol"][-4:] == "USDT"
            ]

            logger.debug(f"Ticker of interest: {tickersOfInterest}")

            # filteredTickers = await self.leverageTickers(tickersOfInterest)

            logger.debug("Fetching last 15 minutes klines...")
            klinesFetcher = KLinesFetcher(
                self._bncClient,
                self._accessKey,
                self._secretKey,
            )
            await klinesFetcher.fetchAllTickersKLines(tickersOfInterest)
            self._klines = klinesFetcher.getKLines()
            logger.debug("Showing last 15 minutes klines")
            logger.debug(self._klines)
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
