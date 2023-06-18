import logging

logger = logging.getLogger(__name__)


class KLine:
    def __init__(self, symbol, openTimestamp, closeTimestamp, open, close):
        self._symbol = symbol
        self._openTimestamp = openTimestamp
        self._closeTimestamp = closeTimestamp
        self._open = open
        self._close = close

    def getSymbol(self):
        return self._symbol

    def getOpenTimestamp(self):
        return self._openTimestamp

    def getCloseTimestamp(self):
        return self._closeTimestamp

    def getOpen(self):
        return self._open

    def getClose(self):
        return self._close

    def __str__(self):
        return f"KLine [symbol={self._symbol}, openTs={self._openTimestamp}, closeTs={self._closeTimestamp},open={self._open},close={self._close}]"

    def __repr__(self):
        return self.__str__()
