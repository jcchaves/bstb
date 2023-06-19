import asyncio
from binance import AsyncClient
from dotenv import load_dotenv
import json
import logging
from logging.config import dictConfig
import os
from quart import Quart, request, websocket as qws
from quart_cors import cors
import sys
from threading import Thread
import traceback

from KLinesFetcher import KLinesFetcher
from OperationManager import OperationManager
from OperationOrdersFetcher import OperationOrdersFetcher
from PriceMovementMonitor import PriceMovementMonitor
from WSPriceMovementAlertNotifier import WSPriceMovementAlertNotifier

logger_format = "%(asctime)s:%(threadName)s:%(name)s:%(message)s"
load_dotenv()
dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": logger_format,
                "datefmt": "%Y-%m-%dT%H:%M:%S %z",
            },
        },
        "handlers": {
            "streamHandler": {
                "class": "logging.StreamHandler",
                "level": "DEBUG",
                "formatter": "default",
                "stream": "ext://sys.stdout",
            },
            "fileHandler": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "default",
                "filename": os.getenv("SPOT_TRADER_BOT_LOG_FILENAME"),
                "maxBytes": 1024000,
                "backupCount": 3,
            },
        },
        "loggers": {
            "root": {
                "handlers": ["streamHandler", "fileHandler"],
                "level": "INFO",
            },
            "__main__": {
                "handlers": ["streamHandler", "fileHandler"],
                "level": "INFO",
            },
            "OperationManager": {
                "handlers": ["streamHandler", "fileHandler"],
                "level": "INFO",
            },
            "OperationOrdersFetcher": {
                "handlers": ["streamHandler", "fileHandler"],
                "level": "INFO",
            },
            "KLinesFetcher": {
                "handlers": ["streamHandler", "fileHandler"],
                "level": "INFO",
            },
            "PriceMovementMonitor": {
                "handlers": ["streamHandler", "fileHandler"],
                "level": "INFO",
            },
            "WSPriceMovementAlertNotifier": {
                "handlers": ["streamHandler", "fileHandler"],
                "level": "INFO",
            },
            "binance": {
                "handlers": ["streamHandler", "fileHandler"],
                "level": "ERROR",
            },
            "asyncio": {
                "handlers": ["streamHandler", "fileHandler"],
                "level": "ERROR",
            },
            "quart.app": {"handlers": ["streamHandler"], "level": "DEBUG"},
            "quart.serving": {"handlers": ["streamHandler"], "level": "DEBUG"},
        },
    }
)

logger = logging.getLogger(__name__)

app = Quart(__name__)
app = cors(app, allow_origin="*")


def _start_async():
    loop = asyncio.new_event_loop()
    return loop


def stop_async(loop):
    loop.call_soon_threadsafe(loop.stop)


# _operation_orders_fetcher_loop = _start_async()
# _operation_manager_loop = _start_async()
_price_movement_monitor_loop = _start_async()


def initPriceMovementMonitor(
    mainLoop,
    loop,
    priceMovementAlertNotifier,
    leverageThreshold,
    longerPeriodPercentThreshold,
    shorterPeriodPercentThreshold,
    accessKey,
    secretKey,
):
    asyncio.set_event_loop(loop)

    PriceMovementMonitor(
        mainLoop,
        loop,
        priceMovementAlertNotifier,
        leverageThreshold,
        longerPeriodPercentThreshold,
        shorterPeriodPercentThreshold,
        accessKey,
        secretKey,
    )
    loop.run_forever()


cache = {}


@app.before_serving
async def createOperationThreads():
    try:
        ACCESS_KEY = os.getenv("ACCESS_KEY")
        SECRET_KEY = os.getenv("SECRET_KEY")
        LEVERAGE_THRESHOLD = os.getenv("LEVERAGE_THRESHOLD")
        if LEVERAGE_THRESHOLD is None:
            LEVERAGE_THRESHOLD = 50
        LONGER_PERIOD_PERCENT_THRESHOLD = os.getenv("LONGER_PERIOD_PERCENT_THRESHOLD")
        if LONGER_PERIOD_PERCENT_THRESHOLD is None:
            LONGER_PERIOD_PERCENT_THRESHOLD = 3
        else:
            LONGER_PERIOD_PERCENT_THRESHOLD = int(LONGER_PERIOD_PERCENT_THRESHOLD)
        SHORTER_PERIOD_PERCENT_THRESHOLD = os.getenv("SHORTER_PERIOD_PERCENT_THRESHOLD")
        if SHORTER_PERIOD_PERCENT_THRESHOLD is None:
            SHORTER_PERIOD_PERCENT_THRESHOLD = 1
        else:
            SHORTER_PERIOD_PERCENT_THRESHOLD = int(SHORTER_PERIOD_PERCENT_THRESHOLD)

        # ooft = Thread(target=_operation_orders_fetcher_loop.run_forever)
        # ooft.start()

        # omt = Thread(target=_operation_manager_loop.run_forever)
        # omt.start()
        cache["priceMovementAlertNotifier"] = WSPriceMovementAlertNotifier(
            asyncio.get_event_loop(),
        )

        pmm = Thread(
            target=initPriceMovementMonitor,
            args=(
                asyncio.get_event_loop(),
                _price_movement_monitor_loop,
                cache["priceMovementAlertNotifier"],
                LEVERAGE_THRESHOLD,
                LONGER_PERIOD_PERCENT_THRESHOLD,
                SHORTER_PERIOD_PERCENT_THRESHOLD,
                ACCESS_KEY,
                SECRET_KEY,
            ),
        )
        pmm.start()

        # operationOrdersFetcher = OperationOrdersFetcher(_operation_orders_fetcher_loop)
        # cache["operationManager"] = OperationManager(
        #     bncClient, operationOrdersFetcher, _operation_manager_loop
        # )
        logger.info("Main started")
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        raise e


@app.after_serving
async def releaseOperationThreads():
    # if _operation_orders_fetcher_loop is not None:
    #     stop_async(_operation_orders_fetcher_loop)
    # if _operation_manager_loop is not None:
    #     stop_async(_operation_manager_loop)
    if _price_movement_monitor_loop is not None:
        stop_async(_price_movement_monitor_loop)
    pass


@app.route("/events", methods=["POST"])
async def handleEvents():
    event = await request.get_json()
    logger.info(f"Received event: {event}")
    return event


@app.route("/operations", methods=["POST"])
async def createOperation():
    data = await request.get_json()
    operation = cache["operationManager"].createOperation(data)
    return operation


@app.route("/operations", methods=["GET"])
async def listOperations():
    return cache["operationManager"].listOperations()


@app.websocket("/ws")
async def ws():
    logger.debug("Handle new WS connection....")
    async for message in cache["priceMovementAlertNotifier"].subscribe():
        logger.debug("Received new message...")
        await qws.send(message)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
