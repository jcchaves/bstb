import asyncio
from binance import AsyncClient, BinanceSocketManager, Client
from binance.exceptions import BinanceAPIException
import json
import logging
from KLine import KLine

logger = logging.getLogger(__name__)


class KLinesFetcher:
    def __init__(self, bncClient, accessKey, secretKey):
        self._bncClient = bncClient
        self._accessKey = accessKey
        self._secretKey = secretKey
        self._klines = {}

    def getKLines(self):
        return self._klines

    async def fetchAllTickersKLines(self, tickers):
        # Fetch all tickers
        logger.debug(f"Fetching klines for {len(tickers)} tickers...")
        tickersBatch = []
        batchSize = 0
        for symbol in tickers:
            logger.debug(f"Batching symbol...{symbol}")
            tickersBatch.append(symbol)
            if len(tickersBatch) == 5:
                logger.debug(f"Fetching tickers batch...{tickersBatch}")
                coroutines = [self.fetchKLines(s) for s in tickersBatch]
                await asyncio.gather(
                    *coroutines,
                )
                asyncio.sleep(1)
                tickersBatch.clear()
                batchSize = 0
                logger.debug(f"{len(self._klines.keys())} tickers processed so far...")
            else:
                batchSize = batchSize + 1
        # Last tickers batch
        if len(tickersBatch) > 0:
            logger.debug("Fetching the last tickers batch...")
            await asyncio.gather(
                *[self.fetchKLines(s) for s in tickersBatch],
            )
            logger.debug(f"KLines fetched ...{self._klines}")

    async def fetchKLines(self, symbol):
        logger.debug(f"Fetching klines for symbol '{symbol}'")
        retries = 0
        fetchingKlines = True
        klines = []
        while fetchingKlines and retries < 2:
            try:
                klines = await self._bncClient.get_historical_klines(
                    symbol,
                    Client.KLINE_INTERVAL_1MINUTE,
                    "15 minutes ago UTC",
                )
                fetchingKlines = False
            except Exception as e:
                print(e)
                asyncio.sleep(5)
                self._bncClient = AsyncClient(self._accessKey, self._secretKey)
                retries = retries + 1
                continue

        self._klines[symbol] = [
            KLine(
                symbol,
                kline[0],
                kline[6],
                float(kline[1]),
                float(
                    kline[4],
                ),
            )
            for kline in klines
        ]
