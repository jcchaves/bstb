import argparse
import asyncio
from binance import AsyncClient, BinanceSocketManager
from binance.exceptions import BinanceWebsocketUnableToConnect
from dotenv import load_dotenv
import logging
import os
import requests

logger_format = "%(asctime)s:%(threadName)s:%(message)s"
load_dotenv()


async def main():
    parser = argparse.ArgumentParser(
        prog="account-events-topic",
        description="Topic providing account update events for subscribers",
    )

    parser.add_argument("-l", "--log_filename", default="account-events-topic.log")

    args = parser.parse_args()

    ACCESS_KEY = os.getenv("ACCESS_KEY")
    SECRET_KEY = os.getenv("SECRET_KEY")

    logging.basicConfig(
        filename=args.log_filename,
        format=logger_format,
        level=logging.INFO,
        datefmt="%Y-%m-%dT%H:%M:%S %z",
    )
    logging.info("Main started")
    client = await AsyncClient.create(ACCESS_KEY, SECRET_KEY)
    bm = BinanceSocketManager(client, user_timeout=10)
    # recreation_attempts = 0
    # recreate = True
    # while recreate:
    # try:
    # await receive_messages(bm)
    # start any sockets here, i.e a trade socket
    us = bm.user_socket()
    # then start receiving messages
    async with us as uscm:
        while True:
            msg = await uscm.recv()
            process_message(msg)
        # except BinanceWebsocketUnableToConnect:
        #     # Exponential back-off to restart websocket connection
        #     logging.info("Waiting before next reconnect attempt...")
        #     asyncio.sleep(10)
        #     recreation_attempts += 1
        #     if recreation_attempts > 5:
        #         recreate = False


async def receive_messages(bm):
    pass


def process_message(msg):
    if msg["e"] == "error":
        # close and restart the socket
        logging.error("Websocket connection lost, attempting recoonection...")
    else:
        requests.post(url="http://127.0.0.1:5000/events", json=msg)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
