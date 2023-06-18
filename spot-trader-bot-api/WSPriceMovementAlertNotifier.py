import asyncio
import logging
from typing import AsyncGenerator

logger = logging.getLogger(__name__)


class WSPriceMovementAlertNotifier:
    def __init__(self, mainLoop) -> None:
        self._mainLoop = mainLoop
        self.connections = set()

    def publish(self, message: str) -> None:
        logger.debug("Publishing new message...")
        for connection in self.connections:
            connection.put_nowait(message)
            connection._loop._write_to_self()

    async def subscribe(self) -> AsyncGenerator[str, None]:
        logger.debug("Subscribing new connection...")
        connection = asyncio.Queue()
        self.connections.add(connection)
        try:
            while True:
                logger.debug("Waiting for new message...")
                yield await connection.get()
                logger.debug("Got new message...")
        finally:
            self.connections.remove(connection)
