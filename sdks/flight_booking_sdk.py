from typing import Any
from commons.cores.base_client import BaseAsyncClient


class FlightBookingSdk(BaseAsyncClient):
    def __init__(self, host, port, api_perfix) -> Any:
        super().__call__()
        self.host = host
        self.port = port
        self.api_perfix = api_perfix

    async def get(self, url, **kwargs):
        pass
